"""任务状态端点"""
from fastapi import APIRouter, HTTPException
from app.models.database import LocalSession, Task

router = APIRouter()


@router.get("/api/tasks")
async def list_tasks():
    """列出所有任务"""
    with LocalSession() as db:
        tasks = db.query(Task).order_by(Task.created_at.desc()).limit(50).all()
        return {
            "tasks": [
                {
                    "id": t.id,
                    "template_id": t.template_id,
                    "nl_query": t.nl_query,
                    "status": t.status,
                    "progress": t.progress,
                    "created_at": t.created_at,
                    "completed_at": t.completed_at,
                }
                for t in tasks
            ]
        }


@router.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str):
    with LocalSession() as db:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(404, "任务不存在")
        return {
            "task_id": task.id, "status": task.status,
            "progress": task.progress, "error_message": task.error_message,
            "created_at": task.created_at, "completed_at": task.completed_at,
        }


@router.get("/api/history")
async def list_history(page: int = 1, size: int = 20):
    with LocalSession() as db:
        total = db.query(Task).count()
        tasks = db.query(Task).order_by(Task.created_at.desc()).offset((page - 1) * size).limit(size).all()
        return {
            "total": total, "page": page, "size": size,
            "items": [{"task_id": t.id, "status": t.status, "template_id": t.template_id, "nl_query": t.nl_query, "created_at": t.created_at, "completed_at": t.completed_at} for t in tasks],
        }
