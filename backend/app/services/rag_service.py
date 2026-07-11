"""
RAG service layer.
Implements vector search, LLM-powered context QA, resume analysis, job matching, and job indexing.
Leverages FastEmbed, Qdrant client, and Groq ChatGroq LLM with robust local mock fallbacks.
"""

from uuid import UUID

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from qdrant_client.http import models
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.embeddings.fastembed_client import fastembed_client
from app.ai.vector_store.qdrant_client import qdrant_vector_store
from app.core.config import settings
from app.core.exceptions import NotFoundException
from app.core.logging import get_logger
from app.crud.crud_job import crud_job
from app.models.job import Job
from app.schemas.rag import (
    RagAskResponse,
    RagEmbedJobsResponse,
    RagJobMatchResponse,
    RagSearchResponse,
    RagSearchResponseItem,
)
from app.schemas.resume_analysis import ResumeAnalysisResponse

logger = get_logger(__name__)


class RagService:
    """
    Core RAG service. Coordinates embeddings creation, vector search queries,
    and LLM analysis matching jobs and resumes.
    """

    def __init__(self) -> None:
        self._llm = None
        if settings.GROQ_API_KEY and not settings.GROQ_API_KEY.startswith("your_"):
            try:
                self._llm = ChatGroq(
                    groq_api_key=settings.GROQ_API_KEY,
                    model_name=settings.GROQ_MODEL,
                    temperature=0.2,
                    max_tokens=settings.GROQ_MAX_TOKENS,
                )
            except Exception as e:
                logger.error(f"Failed to initialize Groq LLM for RAG: {e}")

    # ── Job Embedding Pipeline ───────────────────────────────────────────────

    async def embed_jobs(self, db: AsyncSession) -> RagEmbedJobsResponse:
        """
        Embed all active, non-indexed jobs from the relational DB into Qdrant.
        """
        result = await db.execute(select(Job).where(Job.is_active == True))  # noqa: E712
        jobs = list(result.scalars().all())

        if not jobs:
            return RagEmbedJobsResponse(message="No active jobs found to embed.", jobs_embedded=0)

        # If Qdrant is not active, simulate success by marking jobs as indexed
        if not qdrant_vector_store.is_active:
            logger.info("Qdrant not running. Simulating job embedding indexing.")
            for job in jobs:
                job.is_indexed = True
                db.add(job)
            await db.flush()
            return RagEmbedJobsResponse(
                message="[Simulated] Qdrant offline. Relational DB jobs marked as indexed.",
                jobs_embedded=len(jobs),
            )

        points = []
        for job in jobs:
            # Build indexable text context
            skills = ", ".join(job.skills_required or [])
            job_text = (
                f"Title: {job.title}\n"
                f"Company: {job.company}\n"
                f"Location: {job.location or 'Remote'}\n"
                f"Description: {job.description}\n"
                f"Requirements: {job.requirements or ''}\n"
                f"Skills: {skills}"
            )

            vector = fastembed_client.embed_query(job_text)
            payload = {
                "id": str(job.id),
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "description": job.description,
            }

            points.append(
                models.PointStruct(
                    id=str(job.id).replace("-", ""),  # Qdrant UUID format without dashes or int
                    vector=vector,
                    payload=payload,
                )
            )

        success = await qdrant_vector_store.upsert_points(settings.QDRANT_COLLECTION_JOBS, points)
        if success:
            for job in jobs:
                job.is_indexed = True
                db.add(job)
            await db.flush()
            return RagEmbedJobsResponse(
                message="Jobs embedded and indexed in Qdrant successfully.",
                jobs_embedded=len(jobs),
            )
        else:
            return RagEmbedJobsResponse(message="Failed to index jobs in Qdrant.", jobs_embedded=0)

    # ── Vector Search ─────────────────────────────────────────────────────────

    async def search_jobs(self, db: AsyncSession, *, query: str, limit: int = 5) -> RagSearchResponse:
        """
        Query Qdrant vector store and resolve corresponding database Job records.
        """
        if not qdrant_vector_store.is_active:
            # Fallback to database text search
            logger.info("Qdrant offline. Using database relational fallback for RAG search.")
            total, jobs = await crud_job.get_multi_filtered(db, limit=limit, search=query)
            items = [
                RagSearchResponseItem(job=job, score=0.85 - (i * 0.05))
                for i, job in enumerate(jobs)
            ]
            return RagSearchResponse(items=items)

        query_vector = fastembed_client.embed_query(query)
        points = await qdrant_vector_store.search_similarity(
            settings.QDRANT_COLLECTION_JOBS, query_vector, limit=limit
        )

        items = []
        for point in points:
            job_id_str = point.payload.get("id")
            if job_id_str:
                job = await crud_job.get(db, job_id_str)
                if job:
                    items.append(RagSearchResponseItem(job=job, score=point.score))

        return RagSearchResponse(items=items)

    # ── RAG QA (Ask) ─────────────────────────────────────────────────────────

    async def ask(self, db: AsyncSession, *, question: str) -> RagAskResponse:
        """
        Perform RAG to answer user questions using retrieved jobs as context.
        """
        search_res = await self.search_jobs(db, query=question, limit=3)
        context_jobs = [item.job for item in search_res.items]

        if not context_jobs:
            return RagAskResponse(
                answer="I couldn't find any job listings matching your query to analyze.",
                context_jobs=[],
            )

        if not self._llm:
            # Fallback response
            logger.info("Groq offline. Using mock RAG response generator.")
            titles = [f"'{j.title}' at {j.company}" for j in context_jobs]
            answer = (
                f"Based on the available job database, the most relevant listings matching your question are: "
                f"{', '.join(titles)}. Unfortunately, active Groq LLM integration is not configured, but you can "
                f"browse these job postings directly."
            )
            return RagAskResponse(answer=answer, context_jobs=context_jobs)

        # Build context string
        context_str = ""
        for i, job in enumerate(context_jobs, 1):
            context_str += (
                f"Job {i}:\n"
                f"Title: {job.title}\n"
                f"Company: {job.company}\n"
                f"Location: {job.location or 'Remote'}\n"
                f"Description: {job.description}\n"
                f"Requirements: {job.requirements or 'None'}\n\n"
            )

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an AI Job Assistant. Answer the user's question using ONLY the provided job listings context. Be concise and professional."),
            ("user", "Context Jobs:\n{context}\n\nQuestion: {question}"),
        ])

        try:
            chain = prompt | self._llm
            res = await chain.ainvoke({"context": context_str, "question": question})
            return RagAskResponse(answer=str(res.content).strip(), context_jobs=context_jobs)
        except Exception as e:
            logger.error(f"Error during RAG ask LLM call: {e}")
            return RagAskResponse(
                answer="An error occurred while communicating with the AI model.",
                context_jobs=context_jobs,
            )

    # ── Contextual Resume Analysis ──────────────────────────────────────────

    async def analyze_resume_rag(self, db: AsyncSession, *, resume_text: str) -> ResumeAnalysisResponse:
        """
        Perform RAG resume analysis by matching resume text to top jobs,
        identifying real skills gaps for active jobs.
        """
        # Find top jobs matching resume
        search_res = await self.search_jobs(db, query=resume_text, limit=3)
        matching_jobs = [item.job for item in search_res.items]

        # Use first job title or general role
        target_title = matching_jobs[0].title if matching_jobs else "Software Engineer"
        target_desc = matching_jobs[0].description if matching_jobs else "Software development."

        # Leverage the existing resume parser with contextual details
        from app.schemas.resume_analysis import ResumeAnalysisRequest
        from app.services.resume_analysis_service import resume_analysis_service

        request_schema = ResumeAnalysisRequest(
            resume_text=resume_text,
            target_job_title=target_title,
            target_job_description=target_desc,
        )

        return await resume_analysis_service.analyze_resume(request_schema)

    # ── Job Matching ──────────────────────────────────────────────────────────

    async def job_match(
        self, db: AsyncSession, *, resume_text: str, job_id: UUID | str
    ) -> RagJobMatchResponse:
        """
        Analyze a candidate's resume match compatibility against a specific Job.
        """
        job = await crud_job.get(db, job_id)
        if not job:
            raise NotFoundException("Job")

        # Safely parse skills_required if it is a string (SQLite case)
        skills = job.skills_required
        if isinstance(skills, str):
            import json
            try:
                if skills.strip().startswith("[") and skills.strip().endswith("]"):
                    skills = json.loads(skills)
                else:
                    skills = [s.strip() for s in skills.split(",") if s.strip()]
            except Exception:
                skills = []
        elif not skills:
            skills = []

        if not self._llm:
            # Fallback calculations
            logger.info("Groq offline. Generating mock Job Match metrics.")
            resume_lower = resume_text.lower()
            matching = [s for s in skills if s.lower() in resume_lower]
            missing = [s for s in skills if s.lower() not in resume_lower]
            
            # Simple score calculation
            score = 100.0
            score = len(matching) / len(skills) * 100.0 if skills else 75.0

            explanation = (
                f"Candidate matches {len(matching)} out of {len(skills)} required skills for '{job.title}'. "
                f"Demonstrates alignment with the general requirements."
            )

            return RagJobMatchResponse(
                match_score=round(score, 1),
                matching_skills=matching,
                missing_skills=missing,
                explanation=explanation,
            )

        # prompt LLM
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are an ATS Match Engine. Analyze the resume against the job details and return a strictly formatted JSON output:\n"
                "{{\n"
                '  "match_score": 85.0,\n'
                '  "matching_skills": ["Python", "FastAPI"],\n'
                '  "missing_skills": ["Docker"],\n'
                '  "explanation": "Summarized reason explaining the match compatibility."\n'
                "}}\n"
                "Do not output markdown block fences or text outside JSON structure."
            ),
            (
                "user",
                "Job:\nTitle: {title}\nDescription: {desc}\nSkills Required: {skills}\n\nResume:\n{resume}"
            ),
        ])

        try:
            import json
            chain = prompt | self._llm
            res = await chain.ainvoke({
                "title": job.title,
                "desc": job.description,
                "skills": ", ".join(skills),
                "resume": resume_text,
            })
            content = str(res.content).strip()
            if content.startswith("```"):
                content = content.replace("```json", "", 1).replace("```", "", 1).strip()
            
            data = json.loads(content)
            return RagJobMatchResponse(
                match_score=float(data.get("match_score", 0.0)),
                matching_skills=data.get("matching_skills", []),
                missing_skills=data.get("missing_skills", []),
                explanation=data.get("explanation", "Parsed successfully."),
            )
        except Exception as e:
            logger.error(f"Error during job match LLM call: {e}")
            return RagJobMatchResponse(
                match_score=50.0,
                matching_skills=[],
                missing_skills=skills,
                explanation="Could not generate AI analysis due to API failure.",
            )


# Service singleton
rag_service = RagService()
