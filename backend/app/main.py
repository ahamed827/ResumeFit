import os
from contextlib import asynccontextmanager

# Ensure all models are registered with Base metadata
import app.models  # noqa: F401
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.core.logging import StructuredLoggingMiddleware, logger
from app.db.base import Base
from app.db.session import async_engine
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist in dev/test mode
    logger.info(f"Starting {settings.PROJECT_NAME} in [{settings.ENVIRONMENT}] environment.")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schemas verified.")

    # Create default admin user if not exists
    try:
        from app.core.security import get_password_hash
        from app.db.session import AsyncSessionLocal
        from app.models.user import UserRole
        from app.repositories.user_repository import UserRepository

        async with AsyncSessionLocal() as session:
            repo = UserRepository(session)
            admin = await repo.get_by_email("admin@resumefit.io")
            if not admin:
                await repo.create(
                    email="admin@resumefit.io",
                    password_hash=get_password_hash("AdminPass123!"),
                    full_name="Platform Administrator",
                    role=UserRole.ADMIN,
                )
                await session.commit()
                logger.info("Default admin user provisioned: admin@resumefit.io / AdminPass123!")
    except Exception as e:
        logger.warning(f"Admin auto-provision check skipped or failed: {e}")

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.PROJECT_NAME}...")
    await async_engine.dispose()
    logger.info("Database connections closed.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="AI-powered Resume-to-Job Matcher & Application Tracking Platform",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Exception handlers
register_exception_handlers(app)

# Structured Logging Middleware
app.add_middleware(StructuredLoggingMiddleware)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount local upload directory if local storage
if settings.STORAGE_BACKEND == "local":
    uploads_dir = os.path.abspath(settings.LOCAL_STORAGE_DIR)
    os.makedirs(uploads_dir, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")


# Health endpoints
@app.get("/health", tags=["Health"], status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/ready", tags=["Health"], status_code=status.HTTP_200_OK)
async def readiness_check():
    # Verify DB connectivity
    try:
        async with async_engine.connect() as conn:
            await conn.execute(Base.metadata.tables["users"].select().limit(1))
        db_ready = True
    except Exception:
        db_ready = False

    return {"ready": db_ready, "database": "connected" if db_ready else "unreachable"}


# Include API v1 Router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
