"""
Resume analysis service layer.
Uses LangChain and Groq LLM to parse and extract structured analysis from resume text.
Provides a mock fallback for offline development and testing stability.
"""

import json

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.resume_analysis import ResumeAnalysisRequest, ResumeAnalysisResponse

logger = get_logger(__name__)


class ResumeAnalysisService:
    """
    Coordinates LangChain prompting and Groq LLM invocation to analyze resumes.
    """

    def __init__(self) -> None:
        self._llm = None
        # Initialize Groq client only if API key is provided and valid
        if settings.GROQ_API_KEY and not settings.GROQ_API_KEY.startswith("your_"):
            try:
                self._llm = ChatGroq(
                    groq_api_key=settings.GROQ_API_KEY,
                    model_name=settings.GROQ_MODEL,
                    temperature=0.2,
                    max_tokens=settings.GROQ_MAX_TOKENS,
                )
            except Exception as e:
                logger.error(f"Failed to initialize Groq LLM: {e}")

    async def analyze_resume(self, schema: ResumeAnalysisRequest) -> ResumeAnalysisResponse:
        """
        Analyze resume text and extract skills, experience, missing skills, and recommendations.
        """
        # If LLM client is not initialized, use the mock fallback
        if not self._llm:
            logger.info("Groq API key not configured or failed initialization. Using mock resume analysis fallback.")
            return self._get_mock_analysis(schema)

        system_prompt = (
            "You are an expert ATS (Applicant Tracking System) and professional career optimizer. "
            "Analyze the candidate's resume text and structure the feedback as a JSON object.\n\n"
            "Respond ONLY with a valid JSON object matching the following structure:\n"
            "{{\n"
            '  "extracted_skills": ["list", "of", "extracted", "skills"],\n'
            '  "experience": "A clear description summarizing years of experience and job roles.",\n'
            '  "missing_skills": ["list", "of", "missing", "skills", "for", "the", "target", "role"],\n'
            '  "recommendations": ["actionable", "recommendations", "to", "improve", "the", "profile"]\n'
            "}}\n\n"
            "Do not include any conversational filler, markdown formatting (like ```json), or text outside the JSON object."
        )

        user_prompt = (
            "Resume Text:\n{resume_text}\n\n"
            "Target Job Title: {target_title}\n"
            "Target Job Description:\n{target_desc}\n"
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", user_prompt),
        ])

        target_title = schema.target_job_title or "Software Engineer"
        target_desc = schema.target_job_description or "General software development roles."

        # Bind parameters
        chain = prompt | self._llm

        try:
            response = await chain.ainvoke({
                "resume_text": schema.resume_text,
                "target_title": target_title,
                "target_desc": target_desc,
            })
            content = str(response.content).strip()

            # Clean any markdown fences if the LLM output includes them
            if content.startswith("```"):
                content = content.replace("```json", "", 1).replace("```", "", 1).strip()

            data = json.loads(content)
            return ResumeAnalysisResponse(
                extracted_skills=data.get("extracted_skills", []),
                experience=data.get("experience", "Not specified."),
                missing_skills=data.get("missing_skills", []),
                recommendations=data.get("recommendations", []),
            )

        except Exception as exc:
            logger.error(f"Error invoking Groq LLM or parsing response: {exc}. Falling back to mock analysis.")
            return self._get_mock_analysis(schema)

    def _get_mock_analysis(self, schema: ResumeAnalysisRequest) -> ResumeAnalysisResponse:
        """
        Generate high-quality simulated resume analysis results.
        """
        resume_text_lower = schema.resume_text.lower()
        
        # Simple heuristic skill extractor
        potential_skills = [
            "python", "javascript", "typescript", "react", "fastapi", "postgresql",
            "docker", "kubernetes", "aws", "git", "langchain", "qdrant", "groq"
        ]
        extracted = [skill.capitalize() for skill in potential_skills if skill in resume_text_lower]
        
        # Default skills if none matched
        if not extracted:
            extracted = ["Python", "Git", "Software Development"]

        # Simple heuristic experience summarizer
        years = "3+"
        if "senior" in resume_text_lower or "lead" in resume_text_lower:
            years = "7+"
        elif "junior" in resume_text_lower or "intern" in resume_text_lower:
            years = "1-2"

        experience = f"Estimated {years} years of professional experience in software development, including roles matching general tech stacks."

        # Heuristic missing skills based on target parameters or common developer stacks
        target_title = (schema.target_job_title or "Software Engineer").lower()
        missing = []
        if "react" in target_title and "React" not in extracted:
            missing.append("React")
        if "fastapi" in target_title and "Fastapi" not in extracted:
            missing.append("FastAPI")
        if "docker" in target_title and "Docker" not in extracted:
            missing.append("Docker")
        if "aws" in target_title and "Aws" not in extracted:
            missing.append("AWS S3 / EC2")
            
        # Ensure we have some missing skills
        if not missing:
            missing = ["Docker", "AWS", "Kubernetes", "GraphQL"]

        recommendations = [
            f"Tailor your project descriptions to highlight the target role: '{schema.target_job_title or 'Software Developer'}'.",
            f"Add certification or practical projects matching missing skills: {', '.join(missing[:2])}.",
            "List your technical skill matrix at the very top of your resume for higher ATS search scores.",
            "Quantify your accomplishments (e.g., 'reduced query latency by 30%' instead of 'wrote SQL queries')."
        ]

        return ResumeAnalysisResponse(
            extracted_skills=extracted,
            experience=experience,
            missing_skills=missing,
            recommendations=recommendations,
        )


# Service singleton
resume_analysis_service = ResumeAnalysisService()
