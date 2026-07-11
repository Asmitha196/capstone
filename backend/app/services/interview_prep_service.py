"""
Interview Preparation Service.

Derives interview prep content deterministically from job metadata and resume skill gaps.
No LLM, no DB, no external calls — pure Python logic for speed and reliability.

Logic:
  - aptitude_topics   : selected from a role-based keyword map
  - technical_topics  : union of job.skills_required + missing_skills + description keywords
  - communication_topics: fixed set of universal soft-skill topics
  - practice_links    : curated static links grouped by category
"""

from __future__ import annotations

from app.models.job import Job
from app.schemas.interview_prep import InterviewPrepItem, PracticeLinks

# ── Static resource links ─────────────────────────────────────────────────────

_APTITUDE_LINKS: list[str] = [
    "https://www.indiabix.com/aptitude/questions-and-answers/",
    "https://www.geeksforgeeks.org/aptitude-gq/",
    "https://www.freshersworld.com/aptitude-questions",
]

_TECHNICAL_LINKS: list[str] = [
    "https://www.geeksforgeeks.org/",
    "https://leetcode.com/problemset/",
    "https://www.hackerrank.com/domains/tutorials/10-days-of-statistics",
    "https://www.interviewbit.com/practice/",
]

_COMMUNICATION_LINKS: list[str] = [
    "https://www.linkedin.com/learning/topics/communication",
    "https://www.coursera.org/courses?query=communication+skills",
    "https://www.youtube.com/results?search_query=HR+interview+preparation",
]

# ── Universal communication topics ────────────────────────────────────────────

_COMMUNICATION_TOPICS: list[str] = [
    "HR Interview Topics",
    "Communication Skills",
    "Behavioral Questions (STAR Method)",
    "Teamwork & Collaboration",
    "Leadership & Initiative",
    "Presentation Skills",
    "Problem Solving & Critical Thinking",
    "Conflict Resolution",
    "Time Management",
]

# ── Aptitude topic map keyed by role keywords ──────────────────────────────────

_APTITUDE_ROLE_MAP: dict[str, list[str]] = {
    "data": [
        "Quantitative Aptitude",
        "Data Interpretation",
        "Statistics & Probability",
        "Number Series",
        "Percentage & Ratios",
        "Logical Reasoning",
        "Pie Charts & Bar Graphs",
        "Mean, Median, Mode",
    ],
    "machine learning": [
        "Quantitative Aptitude",
        "Probability & Statistics",
        "Matrix Operations",
        "Logical Reasoning",
        "Number Series",
        "Data Interpretation",
    ],
    "ai": [
        "Quantitative Aptitude",
        "Probability",
        "Logical Reasoning",
        "Number Series",
        "Data Interpretation",
        "Analytical Reasoning",
    ],
    "frontend": [
        "Logical Reasoning",
        "Analytical Reasoning",
        "Number Series",
        "Percentage",
        "Pattern Recognition",
        "Visual Reasoning",
    ],
    "backend": [
        "Quantitative Aptitude",
        "Number Series",
        "Percentage",
        "Probability",
        "Time & Work",
        "Logical Reasoning",
        "Data Interpretation",
    ],
    "full stack": [
        "Quantitative Aptitude",
        "Logical Reasoning",
        "Number Series",
        "Percentage",
        "Time & Work",
        "Data Interpretation",
    ],
    "devops": [
        "Quantitative Aptitude",
        "Logical Reasoning",
        "Analytical Reasoning",
        "Number Series",
        "Time & Work",
    ],
    "cloud": [
        "Quantitative Aptitude",
        "Logical Reasoning",
        "Number Series",
        "Percentage",
        "Time & Work",
    ],
    "security": [
        "Logical Reasoning",
        "Analytical Reasoning",
        "Pattern Recognition",
        "Number Series",
        "Probability",
    ],
    "mobile": [
        "Logical Reasoning",
        "Analytical Reasoning",
        "Number Series",
        "Percentage",
        "Pattern Recognition",
    ],
}

_DEFAULT_APTITUDE_TOPICS: list[str] = [
    "Quantitative Aptitude",
    "Number Series",
    "Percentage",
    "Probability",
    "Time & Work",
    "Logical Reasoning",
    "Data Interpretation",
    "Analytical Reasoning",
]

# ── Description keyword → tech topic hints ────────────────────────────────────

_DESC_KEYWORD_MAP: dict[str, str] = {
    "rest": "REST APIs",
    "api": "REST APIs",
    "sql": "SQL & Databases",
    "database": "Database Design",
    "docker": "Docker & Containers",
    "kubernetes": "Kubernetes",
    "aws": "AWS Cloud Services",
    "azure": "Microsoft Azure",
    "gcp": "Google Cloud Platform",
    "ci/cd": "CI/CD Pipelines",
    "git": "Version Control (Git)",
    "agile": "Agile Methodology",
    "microservice": "Microservices Architecture",
    "linux": "Linux Administration",
    "nosql": "NoSQL Databases",
    "redis": "Redis Caching",
    "kafka": "Apache Kafka",
    "graphql": "GraphQL",
    "machine learning": "Machine Learning Fundamentals",
    "deep learning": "Deep Learning",
    "neural": "Neural Networks",
    "nlp": "Natural Language Processing",
    "vector": "Vector Databases",
    "embedding": "Embeddings & Semantic Search",
    "object oriented": "Object-Oriented Programming",
    "oop": "Object-Oriented Programming",
    "data structure": "Data Structures & Algorithms",
    "algorithm": "Data Structures & Algorithms",
    "testing": "Unit Testing & QA",
    "pytest": "Unit Testing (pytest)",
    "typescript": "TypeScript",
    "react": "React",
    "node": "Node.js",
    "system design": "System Design",
}


class InterviewPrepService:
    """
    Generates interview preparation content for a given job + skill gap pair.
    All logic is deterministic — no external calls required.
    """

    def generate(
        self,
        job: Job,
        match_score: float,
        missing_skills: list[str],
    ) -> InterviewPrepItem:
        """
        Build an InterviewPrepItem for a single matched job.

        Args:
            job: The Job ORM object.
            match_score: Computed match score (0–100).
            missing_skills: Skills present in the job but absent in the resume.

        Returns:
            A fully populated InterviewPrepItem.
        """
        aptitude_topics = self._derive_aptitude_topics(job.title or "")
        technical_topics = self._derive_technical_topics(
            skills_required=job.skills_required or [],
            missing_skills=missing_skills,
            description=job.description or "",
        )

        return InterviewPrepItem(
            job_id=str(job.id),
            job_title=job.title,
            company=job.company,
            match_score=round(match_score, 1),
            missing_skills=missing_skills,
            aptitude_topics=aptitude_topics,
            technical_topics=technical_topics,
            communication_topics=_COMMUNICATION_TOPICS,
            practice_links=PracticeLinks(
                aptitude=_APTITUDE_LINKS,
                technical=_TECHNICAL_LINKS,
                communication=_COMMUNICATION_LINKS,
            ),
        )

    # ── Private helpers ───────────────────────────────────────────────────────

    def _derive_aptitude_topics(self, job_title: str) -> list[str]:
        """Select aptitude topics based on role keywords in the job title."""
        title_lower = job_title.lower()
        for keyword, topics in _APTITUDE_ROLE_MAP.items():
            if keyword in title_lower:
                return topics
        return _DEFAULT_APTITUDE_TOPICS

    def _derive_technical_topics(
        self,
        skills_required: list[str],
        missing_skills: list[str],
        description: str,
    ) -> list[str]:
        """
        Build deduplicated technical topic list from:
          1. job.skills_required
          2. missing_skills (skill gaps — prioritised)
          3. description keyword extraction
        """
        seen: set[str] = set()
        topics: list[str] = []

        def _add(item: str) -> None:
            normalised = item.strip()
            if normalised and normalised.lower() not in seen:
                seen.add(normalised.lower())
                topics.append(normalised)

        # 1. Missing skills first (highest priority — candidate needs these)
        for skill in missing_skills:
            _add(skill)

        # 2. All required job skills
        for skill in skills_required:
            _add(skill)

        # 3. Extract hints from job description
        desc_lower = description.lower()
        for keyword, label in _DESC_KEYWORD_MAP.items():
            if keyword in desc_lower:
                _add(label)

        # 4. Always ensure DSA is included
        _add("Data Structures & Algorithms")
        _add("Object-Oriented Programming")
        _add("System Design Basics")

        return topics[:15]  # Cap at 15 topics for readability


# Module-level singleton
interview_prep_service = InterviewPrepService()
