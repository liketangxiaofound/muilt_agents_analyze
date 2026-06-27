"""
通用文件存储工具

提供 Agent 使用的本地文件读写能力。
"""
import logging
import os
import json
import base64
import zipfile
from datetime import datetime

from strands import tool
from dotenv import load_dotenv

load_dotenv()

LOCAL_STORAGE_DIR = os.getenv("APP_STORAGE_DIR", "./local_storage")
os.makedirs(LOCAL_STORAGE_DIR, exist_ok=True)


def process_file_key(file_key: str) -> str:
    """将相对 file_key 转换为本地绝对路径"""
    if not file_key:
        return LOCAL_STORAGE_DIR
    if os.path.isabs(file_key):
        return file_key
    normalized = file_key.lstrip("/").lstrip("\\")
    # 防止二次拼接：如果路径已包含存储目录名，直接用绝对路径
    storage_basename = os.path.basename(LOCAL_STORAGE_DIR.rstrip("/").rstrip("\\"))
    if normalized.startswith(storage_basename + os.sep) or normalized == storage_basename:
        full_path = os.path.abspath(normalized)
    else:
        full_path = os.path.join(LOCAL_STORAGE_DIR, normalized)
    return os.path.normpath(full_path)


def ensure_directory_exists(file_path: str) -> None:
    """确保目标文件所在目录树存在"""
    directory = os.path.dirname(file_path)
    if directory and not os.path.isdir(directory):
        os.makedirs(directory, exist_ok=True)


@tool
def write_local_file(file_key: str, file_content: str) -> str:
    """将内容写入本地文件。支持文本、JSON 等格式。"""
    if not file_key:
        return "错误：文件路径为空"
    if not file_content:
        return "错误：file_content 为空"
    try:
        full_path = process_file_key(file_key)
        ensure_directory_exists(full_path)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(file_content)
        written_size = os.path.getsize(full_path)
        return f"已写入: {full_path} ({len(file_content)} 字符, {written_size} 字节)"
    except Exception as e:
        return f"写入文件错误: {str(e)}"


@tool
def write_local_file_html(file_key: str, file_content: str) -> str:
    """将 HTML 内容写入本地文件，自动补充 .html 扩展名。"""
    if not file_key:
        return "错误：文件路径为空"
    if not file_content:
        return "错误：file_content 为空"
    try:
        full_path = process_file_key(file_key)
        ensure_directory_exists(full_path)
        if not full_path.endswith(".html"):
            full_path += ".html"
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(file_content)
        file_size = os.path.getsize(full_path)
        return f"HTML 已写入: {full_path} ({len(file_content)} 字符, {file_size} 字节)"
    except Exception as e:
        return f"写入 HTML 错误: {str(e)}"


@tool
def get_local_file_metadata(file_key: str) -> str:
    """获取文件元数据：大小、修改时间、类型等。"""
    try:
        full_path = process_file_key(file_key)
        if not os.path.exists(full_path):
            return f"错误：文件不存在: {full_path}"
        stat = os.stat(full_path)
        file_size = stat.st_size
        mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        ext_map = {
            ".html": "text/html", ".json": "application/json", ".zip": "application/zip",
            ".xlsx": "spreadsheet", ".csv": "text/csv", ".docx": "document", ".pdf": "application/pdf",
        }
        content_type = next((v for k, v in ext_map.items() if full_path.endswith(k)), "application/octet-stream")
        lines = [
            f"文件路径: {full_path}",
            f"文件大小: {file_size} 字节 ({file_size / 1024:.1f} KB)",
            f"修改时间: {mtime}",
            f"文件类型: {content_type}",
        ]
        return "\n".join(lines)
    except Exception as e:
        return f"获取元数据错误: {str(e)}"


@tool
def read_local_file(file_key: str) -> str:
    """读取本地文件内容。文本文件返回原文，二进制文件返回 base64。"""
    try:
        full_path = process_file_key(file_key)
        if not os.path.exists(full_path):
            return f"错误：文件不存在: {full_path}"
        is_binary = any(full_path.endswith(ext) for ext in
                        [".zip", ".xlsx", ".xls", ".docx", ".pdf", ".png", ".jpg"])
        if is_binary:
            with open(full_path, "rb") as f:
                content = base64.b64encode(f.read()).decode("utf-8")
            return content
        else:
            with open(full_path, "r", encoding="utf-8") as f:
                return f.read()
    except Exception as e:
        return f"读取文件错误: {str(e)}"


@tool
def write_local_file_zip(file_key: str, html_files_json: str) -> str:
    """将多个 HTML 文件内容打包为 ZIP。"""
    if not file_key:
        return "错误：文件路径为空"
    if not html_files_json:
        return "错误：html_files_json 为空"
    try:
        files = json.loads(html_files_json)
        if not isinstance(files, list):
            return "错误：html_files_json 应为 JSON 数组"
        full_path = process_file_key(file_key)
        ensure_directory_exists(full_path)
        if not full_path.endswith(".zip"):
            full_path += ".zip"
        with zipfile.ZipFile(full_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for item in files:
                fname = item.get("filename", "report.html")
                content = item.get("content", "")
                zf.writestr(fname, content.encode("utf-8"))
        zip_size = os.path.getsize(full_path)
        return f"ZIP 已创建: {full_path} ({len(files)} 个文件, {zip_size} 字节)"
    except json.JSONDecodeError as e:
        return f"JSON 解析错误: {str(e)}"
    except Exception as e:
        return f"创建 ZIP 错误: {str(e)}"
