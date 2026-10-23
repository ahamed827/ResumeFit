import uuid

from app.api.deps import get_current_user
from app.core.rate_limiter import rate_limiter
from app.db.session import get_db
from app.models.user import User
from app.schemas.match import MatchCreateRequest, MatchListResponse, MatchResponse
from app.services.matching_engine import MatchingEngine
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/matches", tags=["Matching"])


@router.post("", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
async def create_match(
    req: MatchCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Rate limit: 20 match requests per hour per user
    await rate_limiter.check_rate_limit(
        f"rate:match:{current_user.id}", max_requests=20, window_seconds=3600
    )

    engine = MatchingEngine(db)
    return await engine.create_and_run_match(current_user.id, req.resume_id, req.job_id)


@router.get("", response_model=MatchListResponse, status_code=status.HTTP_200_OK)
async def list_matches(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    engine = MatchingEngine(db)
    items, total = await engine.list_matches(current_user.id, skip=skip, limit=limit)
    return MatchListResponse(items=items, total=total, page=(skip // limit) + 1, size=limit)


@router.get("/{match_id}", response_model=MatchResponse, status_code=status.HTTP_200_OK)
async def get_match(
    match_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    engine = MatchingEngine(db)
    return await engine.get_match(match_id, current_user.id)


@router.delete("/{match_id}", status_code=status.HTTP_200_OK)
async def delete_match(
    match_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    engine = MatchingEngine(db)
    await engine.delete_match(match_id, current_user.id)
    return {"message": "Match report deleted successfully."}


@router.post(
    "/{match_id}/improvement-plan", response_model=MatchResponse, status_code=status.HTTP_200_OK
)
async def refresh_improvement_plan(
    match_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    engine = MatchingEngine(db)
    match_data = await engine.get_match(match_id, current_user.id)
    return await engine.create_and_run_match(
        current_user.id, match_data.resume_id, match_data.job_id
    )
