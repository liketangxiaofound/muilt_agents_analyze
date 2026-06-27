"""文件上传端点"""
import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.database import LocalSession, Upload
from app.config.setting import settings
from app.tools.storage_tools import process_file_key

router = APIRouter()
MAX_SIZE = settings.max_upload_size_mb * 1024 * 1024
ALLOWED = settings.allowed_file_types


@router.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """上传文件，返回 file_id 和基本信息"""
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED:
        raise HTTPException(400, f"不支持的文件类型 .{ext}，允许: {ALLOWED}")

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(400, f"文件过大（{len(content)} 字节），上限 {MAX_SIZE} 字节")

    session_id = uuid.uuid4().hex[:8]
    upload_id = uuid.uuid4().hex[:12]
    file_name = f"{upload_id}_{file.filename}"
    rel_path = f"uploads/{session_id}/{file_name}"
    abs_path = process_file_key(rel_path)

    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "wb") as f:
        f.write(content)

    with LocalSession() as db:
        upload = Upload(
            id=upload_id, filename=file.filename, file_type=ext,
            file_size=len(content), file_path=rel_path, session_id=session_id,
        )
        db.add(upload)
        db.commit()

    return {
        "file_id": upload_id, "filename": file.filename,
        "file_type": ext, "file_size": len(content), "session_id": session_id,
    }
