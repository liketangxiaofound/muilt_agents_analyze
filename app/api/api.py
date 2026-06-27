"""核心 API 端点：发起分析、反馈、模板管理"""
import os
import json
import logging
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from app.models.database import LocalSession, Upload, Task, Report
from app.config.template_loader import get_template, list_templates

router = APIRouter()


class AnalysisRequest(BaseModel):
    file_ids: List[str]
    template_id: Optional[str] = None
    nl_query: Optional[str] = None


class FeedbackRequest(BaseModel):
    satisfaction: str = "partial"
    missing_items: List[str] = []
    description: Optional[str] = None


@router.get("/")
async def root():
    return {"message": "Multi-Agent Data Analysis Platform", "version": "1.0.0"}


@router.get("/api/templates")
async def get_templates():
    return {"templates": list_templates()}


@router.post("/api/analysis/run")
async def run_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    if not request.file_ids:
        raise HTTPException(400, "至少需要上传一个文件")
    if not request.template_id and not request.nl_query:
        raise HTTPException(400, "请选择分析模板或输入分析需求")

    with LocalSession() as db:
        uploads = db.query(Upload).filter(Upload.id.in_(request.file_ids)).all()
        if len(uploads) != len(request.file_ids):
            raise HTTPException(404, "部分文件未找到")
        file_paths = [u.file_path for u in uploads]
        file_names = [u.filename for u in uploads]

        import uuid
        task_id = uuid.uuid4().hex[:12]
        task = Task(
            id=task_id, upload_ids=json.dumps(request.file_ids),
            template_id=request.template_id, nl_query=request.nl_query,
            status="pending", progress="任务已创建",
        )
        db.add(task)
        db.commit()

    background_tasks.add_task(
        _execute_analysis, task_id=task_id,
        file_paths=file_paths, file_names=file_names,
        template_id=request.template_id, nl_query=request.nl_query,
    )
    return {"task_id": task_id, "status": "pending"}


@router.post("/api/feedback/{task_id}")
async def submit_feedback(task_id: str, request: FeedbackRequest):
    with LocalSession() as db:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(404, "任务不存在")
        analysis_config = json.loads(task.analysis_config or "{}")
        upload_ids = json.loads(task.upload_ids or "[]")
        uploads = db.query(Upload).filter(Upload.id.in_(upload_ids)).all()
        file_paths = [u.file_path for u in uploads]
        file_names = [u.filename for u in uploads]

    import uuid
    new_task_id = uuid.uuid4().hex[:12]
    with LocalSession() as db:
        new_task = Task(
            id=new_task_id, upload_ids=json.dumps(upload_ids),
            template_id=task.template_id,
            nl_query=f"用户反馈: {request.description or ''}，缺失: {request.missing_items}",
            status="pending", progress="基于反馈重新分析",
        )
        db.add(new_task)
        db.commit()

    import asyncio
    asyncio.create_task(_execute_analysis_with_feedback(
        task_id=new_task_id, file_paths=file_paths, file_names=file_names,
        original_config=analysis_config, feedback=request,
    ))
    return {"task_id": new_task_id, "status": "pending", "message": "已基于反馈创建新任务"}


async def _execute_analysis(task_id, file_paths, file_names, template_id, nl_query):
    from app.agents.coordinator_agent import coordinator

    def update_status(status, progress):
        with LocalSession() as db:
            t = db.query(Task).filter(Task.id == task_id).first()
            if t:
                t.status = status
                t.progress = progress
                if status in ("done", "failed"):
                    t.completed_at = datetime.now().isoformat(timespec="seconds")
                db.commit()

    try:
        update_status("parsing", "正在解析文件...")
        # 解析为绝对路径（abspath 确保 resolve 后是绝对路径，避免 tool 层二次拼接）
        from app.tools.storage_tools import process_file_key
        abs_paths = [os.path.abspath(process_file_key(p)) for p in file_paths]
        files_info = "\n".join(f"- {n} (路径: {p})" for n, p in zip(file_names, abs_paths))
        report_path = f"reports/{task_id}/report.html"

        if template_id and not nl_query:
            template = get_template(template_id)
            if template:
                query = (
                    f"请按模板配置执行分析:\n模板: {template['name']}\n"
                    f"分析方法: {template['analysis']['methods']}\n"
                    f"报告模板: {template['report']['template']}\n"
                    f"报告输出路径: {report_path}\n"
                    f"文件列表:\n{files_info}"
                )
            else:
                query = f"分析以下文件，报告输出到 {report_path}:\n{files_info}"
        else:
            query = f"用户需求: {nl_query}\n报告输出路径: {report_path}\n文件列表:\n{files_info}"

        update_status("analyzing", "正在执行分析...")
        response = await coordinator.invoke_async(query)
        logging.info(f"Coordinator 响应长度: {len(str(response))}")

        # 创建 Report 记录
        with LocalSession() as db:
            import uuid as _uuid
            report = Report(
                id=_uuid.uuid4().hex[:12],
                task_id=task_id,
                file_path=report_path,
                title=f"{file_names[0] if file_names else '报告'} — 分析报告",
                summary=str(response)[:500] if response else "",
            )
            db.add(report)
            db.commit()

        update_status("done", "分析完成")
    except Exception as e:
        logging.error(f"分析任务失败: {e}")
        update_status("failed", str(e))


async def _execute_analysis_with_feedback(task_id, file_paths, file_names, original_config, feedback):
    from app.agents.coordinator_agent import coordinator

    def update_status(status, progress):
        with LocalSession() as db:
            t = db.query(Task).filter(Task.id == task_id).first()
            if t:
                t.status = status
                t.progress = progress
                if status in ("done", "failed"):
                    t.completed_at = datetime.now().isoformat(timespec="seconds")
                db.commit()

    try:
        update_status("analyzing", "基于反馈重新分析...")
        # 解析为绝对路径
        from app.tools.storage_tools import process_file_key
        abs_paths = [os.path.abspath(process_file_key(p)) for p in file_paths]
        report_path = f"reports/{task_id}/report.html"
        missing_str = ", ".join(feedback.missing_items) if feedback.missing_items else "无"
        query = (
            f"用户对之前的报告不满意，反馈如下:\n"
            f"满意度: {feedback.satisfaction}\n缺失内容: {missing_str}\n"
            f"详细描述: {feedback.description or '无'}\n\n"
            f"原始分析配置: {json.dumps(original_config, ensure_ascii=False)}\n\n"
            f"报告输出路径: {report_path}\n"
            f"请直接调用 analyzer_agent 追加缺失的分析方法，然后调用 visualizer_agent 重新生成报告。不需要重新解析文件。\n"
            f"文件列表:\n" + "\n".join(f"- {n} (绝对路径: {p})" for n, p in zip(file_names, abs_paths))
        )
        response = await coordinator.invoke_async(query)
        logging.info(f"反馈重跑响应: {len(str(response))} 字符")

        # 创建 Report 记录
        with LocalSession() as db:
            import uuid as _uuid
            report = Report(
                id=_uuid.uuid4().hex[:12],
                task_id=task_id,
                file_path=report_path,
                title=f"反馈修正 — {file_names[0] if file_names else '报告'}",
                summary=str(response)[:500] if response else "",
            )
            db.add(report)
            db.commit()

        update_status("done", "基于反馈重新分析完成")
    except Exception as e:
        logging.error(f"反馈重跑失败: {e}")
        update_status("failed", str(e))
