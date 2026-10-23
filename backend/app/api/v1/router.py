from app.api.v1.endpoints import admin, applications, auth, jobs, matches, resumes, summaries
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(resumes.router)
api_router.include_router(jobs.router)
api_router.include_router(matches.router)
api_router.include_router(applications.router)
api_router.include_router(summaries.router)
api_router.include_router(admin.router)
