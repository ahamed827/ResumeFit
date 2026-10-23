import uuid
from typing import Any, Dict, List, Optional, Tuple

from app.models.audit import AILogStatus, AITaskType, AIUsageLog, AuditLog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class AuditRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_action(
        self,
        action: str,
        entity_type: str,
        user_id: Optional[uuid.UUID] = None,
        entity_id: Optional[str] = None,
        meta_info: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        log = AuditLog(
            id=uuid.uuid4(),
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            meta_info=meta_info,
            ip_address=ip_address,
        )
        self.db.add(log)
        await self.db.flush()
        return log

    async def log_ai_usage(
        self,
        task_type: AITaskType,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        estimated_cost_usd: float,
        latency_ms: int,
        status: AILogStatus,
        user_id: Optional[uuid.UUID] = None,
        error_message: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> AIUsageLog:
        log = AIUsageLog(
            id=uuid.uuid4(),
            user_id=user_id,
            task_type=task_type,
            model_name=model_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            estimated_cost_usd=estimated_cost_usd,
            latency_ms=latency_ms,
            status=status,
            error_message=error_message,
            request_id=request_id,
        )
        self.db.add(log)
        await self.db.flush()
        return log

    async def list_ai_logs(
        self, skip: int = 0, limit: int = 50, task_type: Optional[AITaskType] = None
    ) -> Tuple[List[AIUsageLog], int]:
        base_filter = []
        if task_type:
            base_filter.append(AIUsageLog.task_type == task_type)

        total_stmt = select(func.count(AIUsageLog.id)).where(*base_filter)
        total_res = await self.db.execute(total_stmt)
        total = total_res.scalar_one()

        stmt = (
            select(AIUsageLog)
            .where(*base_filter)
            .order_by(AIUsageLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def get_metrics(self) -> Dict[str, Any]:
        total_ai_stmt = select(func.count(AIUsageLog.id))
        total_ai = (await self.db.execute(total_ai_stmt)).scalar_one() or 0

        success_stmt = select(func.count(AIUsageLog.id)).where(
            AIUsageLog.status == AILogStatus.SUCCESS
        )
        success_ai = (await self.db.execute(success_stmt)).scalar_one() or 0

        success_rate = round((success_ai / total_ai * 100), 2) if total_ai > 0 else 100.0

        avg_latency_stmt = select(func.avg(AIUsageLog.latency_ms))
        avg_latency = (await self.db.execute(avg_latency_stmt)).scalar_one() or 0.0

        avg_cost_stmt = select(func.sum(AIUsageLog.estimated_cost_usd))
        total_cost = (await self.db.execute(avg_cost_stmt)).scalar_one() or 0.0
        avg_cost = float(total_cost / total_ai) if total_ai > 0 else 0.0

        # Failed logs by error summary
        failed_stmt = (
            select(AIUsageLog.error_message, func.count(AIUsageLog.id))
            .where(AIUsageLog.status == AILogStatus.FAILED)
            .group_by(AIUsageLog.error_message)
            .limit(10)
        )
        failed_res = await self.db.execute(failed_stmt)
        failed_by_err = {str(err or "Unknown"): count for err, count in failed_res.all()}

        return {
            "ai_success_rate": success_rate,
            "average_ai_latency_ms": round(float(avg_latency), 2),
            "average_processing_cost_usd": round(avg_cost, 4),
            "failed_jobs_by_error": failed_by_err,
        }
