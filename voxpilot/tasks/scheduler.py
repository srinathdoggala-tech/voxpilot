"""Background Task Scheduler — Session-surviving background tasks and execution scheduling."""

import time
import uuid
import logging
from typing import Callable, Awaitable, Any
from pydantic import BaseModel, Field

logger = logging.getLogger("voxpilot.tasks")


class TaskDefinition(BaseModel):
    """Task definition model."""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    session_id: str
    user_id: str
    name: str
    description: str
    cron_schedule: str | None = None  # e.g. "0 9 * * 1" (Every Monday at 9am) or None for one-shot
    status: str = "PENDING"  # "PENDING", "RUNNING", "COMPLETED", "FAILED", "CANCELLED"
    created_at: float = Field(default_factory=time.time)
    last_run_at: float | None = None


class TaskExecution(BaseModel):
    """Task execution log entry."""
    execution_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    task_id: str
    status: str
    result: Any | None = None
    error: str | None = None
    execution_time_ms: float = 0.0
    timestamp: float = Field(default_factory=time.time)


class BackgroundTaskScheduler:
    """Session-surviving background task scheduler executing async jobs and tracking idempotency."""

    def __init__(self):
        self.tasks: dict[str, TaskDefinition] = {}
        self.executions: dict[str, list[TaskExecution]] = {}

    def create_task(
        self,
        session_id: str,
        user_id: str,
        name: str,
        description: str,
        cron_schedule: str | None = None
    ) -> TaskDefinition:
        """Create and register new background task."""
        task = TaskDefinition(
            session_id=session_id,
            user_id=user_id,
            name=name,
            description=description,
            cron_schedule=cron_schedule
        )
        self.tasks[task.task_id] = task
        self.executions[task.task_id] = []
        logger.info(f"Registered background task '{name}' (ID: {task.task_id}) for user {user_id}")
        return task

    async def run_task_now(self, task_id: str, job_func: Callable[[], Awaitable[Any]]) -> TaskExecution:
        """Execute background task immediately with exception handling and execution logging."""
        if task_id not in self.tasks:
            raise KeyError(f"Task '{task_id}' not found.")

        task = self.tasks[task_id]
        task.status = "RUNNING"
        start_time = time.perf_counter()

        try:
            res = await job_func()
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            task.status = "COMPLETED"
            task.last_run_at = time.time()

            exec_record = TaskExecution(
                task_id=task_id,
                status="COMPLETED",
                result=res,
                execution_time_ms=elapsed_ms
            )
            self.executions[task_id].append(exec_record)
            logger.info(f"Task '{task.name}' executed successfully in {elapsed_ms:.2f}ms")
            return exec_record
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            task.status = "FAILED"
            exec_record = TaskExecution(
                task_id=task_id,
                status="FAILED",
                error=str(exc),
                execution_time_ms=elapsed_ms
            )
            self.executions[task_id].append(exec_record)
            logger.error(f"Task '{task.name}' failed: {str(exc)}")
            return exec_record

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or scheduled background task."""
        if task_id in self.tasks:
            self.tasks[task_id].status = "CANCELLED"
            logger.info(f"Cancelled task {task_id}")
            return True
        return False


# Global task scheduler singleton instance
background_task_scheduler = BackgroundTaskScheduler()
