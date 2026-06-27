"""报告查询端点"""
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from app.models.database import LocalSession, Report
from app.tools.storage_tools import process_file_key

router = APIRouter()


@router.get("/api/reports/{task_id}")
async def get_report(task_id: str):
    with LocalSession() as db:
        report = db.query(Report).filter(Report.task_id == task_id).first()
        if not report:
            raise HTTPException(404, "报告不存在")
        abs_path = process_file_key(report.file_path)
        if not os.path.exists(abs_path):
            raise HTTPException(404, f"报告文件不存在: {abs_path}")
        with open(abs_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())


@router.get("/api/reports/{task_id}/download")
async def download_report(task_id: str):
    with LocalSession() as db:
        report = db.query(Report).filter(Report.task_id == task_id).first()
        if not report:
            raise HTTPException(404, "报告不存在")
        abs_path = process_file_key(report.file_path)
        if not os.path.exists(abs_path):
            raise HTTPException(404, "报告文件不存在")
        return FileResponse(abs_path, filename=f"report_{task_id}.html")
