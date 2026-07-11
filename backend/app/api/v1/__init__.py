from fastapi import APIRouter

from app.api.v1 import auth, interview_prep, jobs, rag, resume_analysis

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(jobs.router)
api_router.include_router(resume_analysis.router)
api_router.include_router(rag.router)
api_router.include_router(interview_prep.router)

# Future routers (uncomment as you build each module):
# from app.api.v1 import users, recommendations, applications, chat
# api_router.include_router(users.router)
# api_router.include_router(recommendations.router)
# api_router.include_router(applications.router)
# api_router.include_router(chat.router)



