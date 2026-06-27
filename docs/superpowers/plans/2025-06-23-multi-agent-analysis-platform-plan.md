# 通用多 Agent 数据分析平台 — 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将现有 IoT 设备监控项目改造为配置驱动、零 IoT 残留的通用多 Agent 数据分析平台。

**Architecture:** 4 个 Strands Agent（Coordinator / Fetcher / Analyzer / Visualizer）+ YAML 分析模板系统 + SQLite 元数据管理 + FastAPI 7 端点 + 本地文件存储。Coordinator 接收模板或自然语言 → 调度子 Agent → 生成 HTML 报告 → 支持反馈重跑。

**Tech Stack:** Strands Agents, FastAPI, SQLAlchemy (SQLite), Pydantic, Jinja2, Chart.js, openpyxl, python-docx, pypdf

---

## 文件结构总览

改造后的完整目录树（仅列出保留和新建的文件）：

```
mutli-agents/
├── main.py                          # FastAPI 入口（微调）
├── run.py                           # 启动脚本（不动）
├── config.yml                       # 通用配置（重写自 config_dev.yml）
├── .env.example                     # 环境变量模板（微调）
├── requirements.txt                 # 补充依赖
│
├── app/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── coordinator_agent.py     # 新建
│   │   ├── fetcher_agent.py         # 新建
│   │   ├── analyzer_agent.py        # 新建
│   │   └── visualizer_agent.py      # 新建
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── file_tools.py            # 新建
│   │   ├── analysis_tools.py        # 新建
│   │   ├── viz_tools.py             # 新建
│   │   ├── storage_tools.py         # 从 strands_agents_tool 迁移通用函数
│   │   └── email_tools.py           # 从 strands_agents_tool 迁移 send_email
│   │
│   ├── prompt/
│   │   ├── __init__.py
│   │   ├── coordinator_prompt.py    # 新建
│   │   ├── fetcher_prompt.py        # 新建
│   │   ├── analyzer_prompt.py       # 新建
│   │   └── visualizer_prompt.py     # 新建
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── LLM_model.py             # 保留
│   │   └── database.py              # 新建
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── api.py                   # 重写
│   │   ├── upload.py                # 新建
│   │   ├── tasks.py                 # 新建
│   │   └── reports.py               # 新建
│   │
│   └── config/
│       ├── __init__.py
│       ├── setting.py               # 精简自 setting_env.py
│       └── template_loader.py       # 新建
│
├── templates/                       # 新建目录
│   ├── statistical_summary.yml
│   ├── text_extraction.yml
│   ├── comparative_analysis.yml
│   ├── financial_audit.yml
│   ├── performance_review.yml
│   └── comprehensive_report.yml
│
├── report_templates/                # 新建目录
│   ├── executive_dashboard.html
│   └── minimal_report.html
│
└── examples/                        # 新建目录
    ├── sample_sales.xlsx
    ├── sample_report.docx
    └── README.md
```

---

## 阶段 1：拆除 — 删除所有 IoT 残留

### Task 1.1: 删除 IoT 专用 Agent 和 Prompt 文件

**Files:**
- Delete: `app/agents/lead_agent.py`
- Delete: `app/agents/data_query_agent.py`
- Delete: `app/agents/data_analyst_agent.py`
- Delete: `app/agents/web_engineer_agent.py`
- Delete: `app/agents/html_report_review_agent.py`
- Delete: `app/agents/summary_html_agent.py`
- Delete: `app/agents/zip_file_agent.py`
- Delete: `app/agents/send_email_agent.py`
- Delete: `app/prompt/lead_prompt.py`
- Delete: `app/prompt/data_query_prompt.py`
- Delete: `app/prompt/data_analyst_prompt.py`
- Delete: `app/prompt/web_engieer_prompt.py`
- Delete: `app/prompt/html_report_review_prompt.py`
- Delete: `app/prompt/summary_html_prompt.py`
- Delete: `app/prompt/zip_file_prompt.py`
- Delete: `app/prompt/send_email_prompt.py`

- [ ] **Step 1: 删除所有 IoT Agent 文件**

```bash
rm app/agents/lead_agent.py
rm app/agents/data_query_agent.py
rm app/agents/data_analyst_agent.py
rm app/agents/web_engineer_agent.py
rm app/agents/html_report_review_agent.py
rm app/agents/summary_html_agent.py
rm app/agents/zip_file_agent.py
rm app/agents/send_email_agent.py
```

- [ ] **Step 2: 删除所有 IoT Prompt 文件**

```bash
rm app/prompt/lead_prompt.py
rm app/prompt/data_query_prompt.py
rm app/prompt/data_analyst_prompt.py
rm app/prompt/web_engieer_prompt.py
rm app/prompt/html_report_review_prompt.py
rm app/prompt/summary_html_prompt.py
rm app/prompt/zip_file_prompt.py
rm app/prompt/send_email_prompt.py
```

- [ ] **Step 3: 验证 agents/ 和 prompt/ 只保留 __init__.py**

```bash
ls app/agents/     # 应仅显示 __init__.py
ls app/prompt/     # 应仅显示 __init__.py
```

---

### Task 1.2: 删除 IoT 专用数据库、服务和配置文件

**Files:**
- Delete: `app/db/mysql/live_connection_log.py`
- Delete: `app/db/mysql/live_connection_statistic_rate_5m.py`
- Delete: `app/db/mysql/live_connection_statistics_speed_5m.py`
- Delete: `app/db/mysql/__init__.py`
- Delete: `app/db/__init__.py`
- Delete: `app/servics/get_device_model.py`
- Delete: `app/servics/get_date.py`
- Delete: `app/servics/mysql_service.py`
- Delete: `app/servics/__init__.py`
- Delete: `app/config/setting_env.py`
- Delete: `app/config/setting_sql.py`
- Delete: `config_dev.yml`
- Delete: `app/tools/strands_agents_tool.py`

- [ ] **Step 1: 删除 IoT 数据库模型和空目录**

```bash
rm -rf app/db/
rm -rf app/servics/
```

- [ ] **Step 2: 删除 IoT 配置文件**

```bash
rm app/config/setting_env.py
rm app/config/setting_sql.py
rm config_dev.yml
```

- [ ] **Step 3: 删除 IoT 工具文件（稍后从其中提取通用函数到新文件）**

```bash
rm app/tools/strands_agents_tool.py
```

- [ ] **Step 4: 删除空目录残留**

```bash
rmdir mutli-agents 2>/dev/null || true
```

- [ ] **Step 5: 验证关键目录状态**

```bash
ls app/db/ 2>/dev/null && echo "ERROR: db/ should not exist" || echo "OK: db/ removed"
ls app/servics/ 2>/dev/null && echo "ERROR: servics/ should not exist" || echo "OK: servics/ removed"
ls app/config/  # 应仅显示 __init__.py
ls app/tools/   # 应仅显示 __init__.py
```

Expected output:
```
OK: db/ removed
OK: servics/ removed
__init__.py
__init__.py
```

- [ ] **Step 6: 提交**

```bash
git add -A
git commit -m "feat: remove all IoT-specific code (agents, prompts, db, services, config)

- Delete 8 IoT-specific agent files
- Delete 8 IoT-specific prompt files
- Delete 3 IoT MySQL table models and db/ directory
- Delete servics/ directory (device model, date, mysql service)
- Delete setting_env.py, setting_sql.py, config_dev.yml
- Delete strands_agents_tool.py (will be replaced with modular tools)

Prepares codebase for generic multi-agent analysis platform rebuild."
```

---

## 阶段 2：基础 — 新建配置、数据库、目录结构

### Task 2.1: 创建通用配置文件

**Files:**
- Create: `config.yml`
- Modify: `app/config/__init__.py`

- [ ] **Step 1: 创建 `config.yml`**

```yaml
# 通用多 Agent 数据分析平台配置文件
# 使用方式: python run.py

port: 8000
version: "1.0.0"

# 本地存储根目录（上传文件、提取数据、生成报告的存放位置）
storage_dir: "./local_storage"

# 报告保留天数（超期自动清理）
report_retention_days: 30

# 上传文件限制
max_upload_size_mb: 20
allowed_file_types:
  - xlsx
  - xls
  - csv
  - docx
  - pdf
```

- [ ] **Step 2: 创建 `app/config/setting.py`**

```python
"""
应用配置管理

优先级: 命令行参数 > 环境变量 > config.yml 默认值
"""
import os
import sys
from pathlib import Path
from typing import Optional, List

from pydantic import BaseModel
from pydantic_settings import BaseSettings
from yaml import safe_load


class Setting(BaseSettings):
    port: int = 8000
    version: str = "1.0.0"
    storage_dir: str = "./local_storage"
    report_retention_days: int = 30
    max_upload_size_mb: int = 20
    allowed_file_types: List[str] = ["xlsx", "xls", "csv", "docx", "pdf"]

    class Config:
        env_prefix = "APP_"
        env_file = ".env"
        extra = "allow"


# 加载 YAML 配置文件
def _load_settings() -> Setting:
    # 确定配置文件
    profile = sys.argv[1] if len(sys.argv) > 1 else None
    project_dir = Path(__file__).parents[2]

    if profile:
        config_file = f"config_{profile}.yml"
    else:
        config_file = "config.yml"

    config_path = project_dir / config_file
    if not config_path.exists():
        print(f"配置文件 {config_path} 不存在，使用默认配置")
        return Setting()

    with open(config_path, "r") as f:
        data = safe_load(f) or {}

    # 环境变量覆盖 YAML
    data["port"] = int(os.getenv("APP_PORT", data.get("port", 8000)))
    data["storage_dir"] = os.getenv("APP_STORAGE_DIR", data.get("storage_dir", "./local_storage"))

    return Setting(**data)


settings = _load_settings()
print(f"配置加载完成: port={settings.port}, storage={settings.storage_dir}")
```

- [ ] **Step 3: 验证配置加载**

```bash
cd C:\Users\YZW04\Desktop\开源技术\mutli-agents-main
python -c "from app.config.setting import settings; print(f'Port: {settings.port}, Storage: {settings.storage_dir}')"
```

Expected output:
```
配置加载完成: port=8000, storage=./local_storage
Port: 8000, Storage: ./local_storage
```

- [ ] **Step 4: 提交**

```bash
git add config.yml app/config/setting.py app/config/__init__.py
git commit -m "feat: add generic config system with YAML + env override"
```

---

### Task 2.2: 创建 SQLite 元数据模型

**Files:**
- Create: `app/models/database.py`

- [ ] **Step 1: 创建 `app/models/database.py`**

```python
"""
SQLite 元数据管理

三张表:
- uploads:  文件上传记录
- tasks:    分析任务记录
- reports:  报告记录
"""
import uuid
import os
from datetime import datetime

from sqlalchemy import (
    Column, String, Integer, Text, Float, ForeignKey,
    create_engine, event
)
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config.setting import settings

# ---- 数据库引擎 ----
DB_PATH = os.path.join(settings.storage_dir, "metadata.db")
os.makedirs(settings.storage_dir, exist_ok=True)

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},
    echo=False,
)

# 启用 WAL 模式以支持并发读写
@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.close()


Base = declarative_base()
LocalSession = sessionmaker(bind=engine)


def gen_id() -> str:
    return uuid.uuid4().hex[:12]


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


# ---- 模型 ----

class Upload(Base):
    __tablename__ = "uploads"

    id          = Column(String, primary_key=True, default=gen_id)
    filename    = Column(String, nullable=False)
    file_type   = Column(String, nullable=False)   # xlsx / csv / docx / pdf
    file_size   = Column(Integer)
    file_path   = Column(String, nullable=False)
    session_id  = Column(String, nullable=False)
    preview     = Column(Text)                     # Fetcher 解析后的预览 JSON
    created_at  = Column(String, nullable=False, default=now_iso)


class Task(Base):
    __tablename__ = "tasks"

    id              = Column(String, primary_key=True, default=gen_id)
    upload_ids      = Column(Text, nullable=False)  # JSON 数组: ["id1", "id2"]
    template_id     = Column(String)                # 模板 ID（自然语言时为空）
    nl_query        = Column(Text)                  # 自然语言需求
    status          = Column(String, nullable=False, default="pending")
    # status: pending / parsing / analyzing / visualizing / done / failed
    progress        = Column(String)                # 当前步骤描述
    analysis_config = Column(Text)                  # Coordinator 生成的配置 JSON
    error_message   = Column(Text)
    created_at      = Column(String, nullable=False, default=now_iso)
    completed_at    = Column(String)


class Report(Base):
    __tablename__ = "reports"

    id          = Column(String, primary_key=True, default=gen_id)
    task_id     = Column(String, ForeignKey("tasks.id"), nullable=False)
    file_path   = Column(String, nullable=False)
    title       = Column(String)
    summary     = Column(Text)
    created_at  = Column(String, nullable=False, default=now_iso)


# ---- 初始化 ----
Base.metadata.create_all(engine)
```

- [ ] **Step 2: 验证数据库创建**

```bash
cd C:\Users\YZW04\Desktop\开源技术\mutli-agents-main
python -c "
from app.models.database import engine, Base, Upload, Task, Report
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f'Tables: {tables}')
assert 'uploads' in tables
assert 'tasks' in tables
assert 'reports' in tables
print('All tables created successfully')
"
```

Expected output:
```
Tables: ['uploads', 'tasks', 'reports']
All tables created successfully
```

- [ ] **Step 3: 提交**

```bash
git add app/models/database.py
git commit -m "feat: add SQLite metadata models (uploads, tasks, reports)"
```

---

### Task 2.3: 补全 __init__.py 文件

**Files:**
- Create: `app/tools/__init__.py`（若不存在则创建）
- Verify: `app/agents/__init__.py`, `app/prompt/__init__.py`, `app/api/__init__.py`, `app/models/__init__.py`, `app/config/__init__.py`

- [ ] **Step 1: 确保所有 __init__.py 存在**

```bash
cd C:\Users\YZW04\Desktop\开源技术\mutli-agents-main
for dir in app app/agents app/tools app/prompt app/models app/api app/config; do
  if [ ! -f "$dir/__init__.py" ]; then
    touch "$dir/__init__.py"
    echo "Created: $dir/__init__.py"
  else
    echo "Exists: $dir/__init__.py"
  fi
done
```

- [ ] **Step 2: 提交**

```bash
git add -A
git commit -m "chore: ensure all __init__.py files exist"
```

---

## 阶段 3：工具层 — 创建 5 个工具模块

### Task 3.1: 创建 storage_tools.py（文件存储工具）

**Files:**
- Create: `app/tools/storage_tools.py`

从已删除的 `strands_agents_tool.py` 中提取通用函数，去掉所有 IoT 专用内容。

- [ ] **Step 1: 创建 `app/tools/storage_tools.py`**

```python
"""
通用文件存储工具

提供 Agent 使用的本地文件读写能力：
- 文件写入（文本 / JSON / HTML / ZIP）
- 文件读取（文本 + 二进制）
- 元数据查询
"""
import logging
import os
import json
import base64
import zipfile
from io import BytesIO
from datetime import datetime
from typing import Optional

from strands import tool
from dotenv import load_dotenv

load_dotenv()

# ---- 存储路径配置 ----
LOCAL_STORAGE_DIR = os.getenv("APP_STORAGE_DIR", "./local_storage")
os.makedirs(LOCAL_STORAGE_DIR, exist_ok=True)


# ============================================================
# 辅助函数
# ============================================================

def process_file_key(file_key: str) -> str:
    """将相对 file_key 转换为本地绝对路径"""
    if not file_key:
        return LOCAL_STORAGE_DIR
    if os.path.isabs(file_key):
        return file_key
    normalized = file_key.lstrip("/").lstrip("\\")
    full_path = os.path.join(LOCAL_STORAGE_DIR, normalized)
    return os.path.normpath(full_path)


def ensure_directory_exists(file_path: str) -> None:
    """确保目标文件所在目录树存在"""
    directory = os.path.dirname(file_path)
    if directory and not os.path.isdir(directory):
        os.makedirs(directory, exist_ok=True)


# ============================================================
# 工具函数
# ============================================================

@tool
def write_local_file(file_key: str, file_content: str) -> str:
    """
    将内容写入本地文件。支持文本、JSON 等格式。

    参数:
        file_key:     文件相对路径，如 "data/result.json"
        file_content: 要写入的内容
    返回:
        写入结果描述
    """
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
        logging.info(f"文件写入成功: {full_path} ({written_size} 字节)")
        return f"已写入: {full_path} ({len(file_content)} 字符, {written_size} 字节)"
    except Exception as e:
        logging.error(f"文件写入失败: {e}")
        return f"写入文件错误: {str(e)}"


@tool
def write_local_file_html(file_key: str, file_content: str) -> str:
    """
    将 HTML 内容写入本地文件，自动补充 .html 扩展名。

    参数:
        file_key:     文件相对路径
        file_content: HTML 内容
    返回:
        写入结果描述
    """
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
    """
    获取文件元数据：大小、修改时间、类型等。

    参数:
        file_key: 文件相对路径
    返回:
        元数据描述文本
    """
    try:
        full_path = process_file_key(file_key)
        if not os.path.exists(full_path):
            return f"错误：文件不存在: {full_path}"

        stat = os.stat(full_path)
        file_size = stat.st_size
        mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")

        if full_path.endswith(".html"):
            content_type = "text/html"
        elif full_path.endswith(".json"):
            content_type = "application/json"
        elif full_path.endswith(".zip"):
            content_type = "application/zip"
        elif full_path.endswith((".xlsx", ".xls")):
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif full_path.endswith(".csv"):
            content_type = "text/csv"
        elif full_path.endswith(".docx"):
            content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif full_path.endswith(".pdf"):
            content_type = "application/pdf"
        else:
            content_type = "application/octet-stream"

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
    """
    读取本地文件内容。文本文件返回原文，二进制文件返回 base64。

    参数:
        file_key: 文件相对路径
    返回:
        文件内容
    """
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
    """
    将多个 HTML 文件内容打包为 ZIP。

    参数:
        file_key:        ZIP 文件相对路径
        html_files_json: JSON 字符串，格式 [{"filename": "a.html", "content": "..."}, ...]
    返回:
        打包结果描述
    """
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
```

- [ ] **Step 2: 语法验证**

```bash
python -m py_compile app/tools/storage_tools.py && echo "OK" || echo "FAIL"
```

Expected: `OK`

- [ ] **Step 3: 提交**

```bash
git add app/tools/storage_tools.py
git commit -m "feat: add storage_tools.py - generic file read/write/zip tools"
```

---

### Task 3.2: 创建 email_tools.py（邮件工具）

**Files:**
- Create: `app/tools/email_tools.py`

从已删除的 `strands_agents_tool.py` 中提取 `send_email` 函数。

- [ ] **Step 1: 创建 `app/tools/email_tools.py`**

```python
"""
邮件发送工具

提供 Agent 使用的 SMTP 邮件发送能力。
所需环境变量: SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SENDER_EMAIL
"""
import os
import ssl
import certifi
import logging
import smtplib
from email.message import EmailMessage
from email.utils import formatdate

from strands import tool
from dotenv import load_dotenv

load_dotenv()


@tool
def send_email(
    subject: str,
    body: str,
    recipient_emails: str,
    attachment_paths: str = "",
) -> str:
    """
    通过 SMTP 发送邮件，支持 HTML 正文和多附件。

    环境变量: SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SENDER_EMAIL

    参数:
        subject:          邮件主题
        body:             邮件正文（支持 HTML）
        recipient_emails: 收件人，逗号分隔
        attachment_paths: 附件路径，逗号分隔（可选）
    返回:
        发送结果描述
    """
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    sender_email = os.getenv("SENDER_EMAIL", "")

    if not smtp_host:
        return "错误：SMTP_HOST 未配置"
    if not smtp_username or not smtp_password:
        return "错误：SMTP 凭据未配置"
    if not sender_email:
        return "错误：SENDER_EMAIL 未配置"
    if not recipient_emails.strip():
        return "错误：收件人为空"

    recipient_list = [a.strip() for a in recipient_emails.split(",") if a.strip()]
    if not recipient_list:
        return "错误：无法解析收件人地址"

    attachment_list = []
    if attachment_paths.strip():
        attachment_list = [p.strip() for p in attachment_paths.split(",") if p.strip()]
        for att in attachment_list:
            if not os.path.exists(att):
                return f"错误：附件不存在: {att}"

    try:
        msg = EmailMessage()
        msg["From"] = sender_email
        msg["To"] = ", ".join(recipient_list)
        msg["Subject"] = subject
        msg["Date"] = formatdate(localtime=True)

        is_html = body.strip().startswith("<!DOCTYPE") or body.strip().startswith("<html")
        if is_html:
            msg.add_alternative(body, subtype="html")
        else:
            msg.set_content(body)

        for att in attachment_list:
            with open(att, "rb") as f:
                file_data = f.read()
            fname = os.path.basename(att)
            if fname.endswith(".html"):
                mt, st = "text", "html"
            elif fname.endswith(".zip"):
                mt, st = "application", "zip"
            elif fname.endswith(".pdf"):
                mt, st = "application", "pdf"
            else:
                mt, st = "application", "octet-stream"
            msg.add_attachment(file_data, maintype=mt, subtype=st, filename=fname)

        context = ssl.create_default_context(cafile=certifi.where())
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)

        return f"邮件已发送: 发件人={sender_email}, 收件人={recipient_list}, 附件={len(attachment_list)}个"
    except smtplib.SMTPAuthenticationError:
        return "错误：SMTP 认证失败，请检查用户名密码"
    except smtplib.SMTPConnectError:
        return f"错误：无法连接 SMTP 服务器 {smtp_host}:{smtp_port}"
    except Exception as e:
        logging.error(f"邮件发送失败: {e}")
        return f"邮件发送错误: {str(e)}"
```

- [ ] **Step 2: 语法验证**

```bash
python -m py_compile app/tools/email_tools.py && echo "OK" || echo "FAIL"
```

- [ ] **Step 3: 提交**

```bash
git add app/tools/email_tools.py
git commit -m "feat: add email_tools.py - SMTP email sending tool"
```

---

### Task 3.3: 创建 file_tools.py（文件解析工具）

**Files:**
- Create: `app/tools/file_tools.py`

- [ ] **Step 1: 创建 `app/tools/file_tools.py`**

```python
"""
文件解析工具

提供多格式文件解析能力，输出统一的数据结构。
"""
import os
import json
import logging
from strands import tool

# ---- Excel 解析 ----
try:
    import openpyxl
except ImportError:
    openpyxl = None

# ---- CSV 解析 ----
import csv
from io import StringIO

# ---- DOCX 解析 ----
try:
    import docx
except ImportError:
    docx = None

# ---- PDF 解析 ----
try:
    import pypdf
except ImportError:
    pypdf = None


def _read_file_bytes(file_path: str) -> bytes:
    """读取文件原始字节，处理相对路径"""
    from app.tools.storage_tools import process_file_key
    full_path = process_file_key(file_path)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"文件不存在: {full_path}")
    with open(full_path, "rb") as f:
        return f.read()


@tool
def parse_excel(file_path: str, sheet_name: str = "") -> str:
    """
    解析 Excel 文件（xlsx/xls），提取所有工作表的表头和数据行。

    参数:
        file_path:  Excel 文件路径
        sheet_name: 工作表名称（留空则读取第一个工作表）
    返回:
        JSON 格式的解析结果
    """
    if openpyxl is None:
        return json.dumps({"error": "openpyxl 未安装，无法解析 Excel 文件"}, ensure_ascii=False)

    try:
        full_path = _resolve_path(file_path)
        wb = openpyxl.load_workbook(full_path, data_only=True)

        sheets_data = []
        target_sheets = [sheet_name] if sheet_name else [wb.sheetnames[0]]

        for sname in target_sheets:
            if sname not in wb.sheetnames:
                continue
            ws = wb[sname]
            rows = list(ws.iter_rows(values_only=True))
            if not rows:
                continue

            headers = [str(h) if h is not None else f"col_{i}" for i, h in enumerate(rows[0])]
            data_rows = []
            for row in rows[1:]:
                data_rows.append([
                    None if cell is None else str(cell) if isinstance(cell, str) else cell
                    for cell in row
                ])

            sheets_data.append({
                "sheet_name": sname,
                "row_count": len(data_rows),
                "column_count": len(headers),
                "columns": headers,
                "rows": data_rows,
            })

        return json.dumps({
            "type": "tabular",
            "source": os.path.basename(file_path),
            "sheets": sheets_data,
        }, ensure_ascii=False, default=str)

    except Exception as e:
        logging.error(f"Excel 解析失败: {e}")
        return json.dumps({"error": f"Excel 解析失败: {str(e)}"}, ensure_ascii=False)


@tool
def parse_csv(file_path: str, delimiter: str = ",", has_header: bool = True) -> str:
    """
    解析 CSV 文件。

    参数:
        file_path:  CSV 文件路径
        delimiter:  分隔符（默认逗号）
        has_header: 是否有表头行
    返回:
        JSON 格式的解析结果
    """
    try:
        full_path = _resolve_path(file_path)
        with open(full_path, "r", encoding="utf-8-sig") as f:
            content = f.read()

        reader = csv.reader(StringIO(content), delimiter=delimiter)
        rows = list(reader)
        if not rows:
            return json.dumps({"error": "CSV 文件为空"}, ensure_ascii=False)

        if has_header:
            headers = rows[0]
            data_rows = rows[1:]
        else:
            headers = [f"col_{i}" for i in range(len(rows[0]))]
            data_rows = rows

        return json.dumps({
            "type": "tabular",
            "source": os.path.basename(file_path),
            "sheets": [{
                "sheet_name": "data",
                "row_count": len(data_rows),
                "column_count": len(headers),
                "columns": headers,
                "rows": data_rows,
            }],
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": f"CSV 解析失败: {str(e)}"}, ensure_ascii=False)


@tool
def parse_docx(file_path: str) -> str:
    """
    解析 Word 文档（docx），提取段落和表格。

    参数:
        file_path: docx 文件路径
    返回:
        JSON 格式的解析结果
    """
    if docx is None:
        return json.dumps({"error": "python-docx 未安装，无法解析 Word 文档"}, ensure_ascii=False)

    try:
        full_path = _resolve_path(file_path)
        document = docx.Document(full_path)

        paragraphs = []
        for para in document.paragraphs:
            text = para.text.strip()
            if text:
                style = para.style.name if para.style else "Normal"
                paragraphs.append({"text": text, "style": style})

        tables = []
        for i, table in enumerate(document.tables):
            headers = []
            rows = []
            for j, row in enumerate(table.rows):
                cells = [cell.text.strip() for cell in row.cells]
                if j == 0:
                    headers = cells
                else:
                    rows.append(cells)
            tables.append({
                "table_index": i,
                "row_count": len(rows),
                "columns": headers,
                "rows": rows,
            })

        return json.dumps({
            "type": "textual",
            "source": os.path.basename(file_path),
            "paragraph_count": len(paragraphs),
            "table_count": len(tables),
            "paragraphs": paragraphs,
            "tables": tables,
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": f"Docx 解析失败: {str(e)}"}, ensure_ascii=False)


@tool
def parse_pdf(file_path: str) -> str:
    """
    解析 PDF 文件，提取文本内容。

    参数:
        file_path: PDF 文件路径
    返回:
        JSON 格式的解析结果
    """
    if pypdf is None:
        return json.dumps({"error": "pypdf 未安装，无法解析 PDF 文件"}, ensure_ascii=False)

    try:
        full_path = _resolve_path(file_path)
        reader = pypdf.PdfReader(full_path)

        pages = []
        full_text = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                text = text.strip()
                pages.append({"page": i + 1, "text": text})
                full_text.append(text)

        return json.dumps({
            "type": "textual",
            "source": os.path.basename(file_path),
            "page_count": len(reader.pages),
            "pages": pages,
            "full_text": "\n\n".join(full_text),
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": f"PDF 解析失败: {str(e)}"}, ensure_ascii=False)


@tool
def detect_structure(parsed_data_json: str) -> str:
    """
    分析已解析数据的结构：识别列类型（数值/分类/日期/文本）。

    参数:
        parsed_data_json: parse_* 工具输出的 JSON 字符串
    返回:
        结构分析结果 JSON
    """
    from datetime import datetime

    try:
        data = json.loads(parsed_data_json)
    except json.JSONDecodeError:
        return json.dumps({"error": "输入不是有效 JSON"}, ensure_ascii=False)

    structure = {"type": data.get("type", "unknown"), "tables_analysis": [], "text_analysis": {}}

    # 分析表格
    for sheet in data.get("sheets", []):
        columns = sheet.get("columns", [])
        rows = sheet.get("rows", [])
        if not columns or not rows:
            continue

        col_types = {}
        for i, col in enumerate(columns):
            values = [row[i] for row in rows if i < len(row) and row[i] is not None]
            if not values:
                col_types[col] = "empty"
                continue

            numeric_count = sum(1 for v in values if isinstance(v, (int, float)))
            date_count = 0
            for v in values:
                if isinstance(v, str):
                    for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d", "%d/%m/%Y"]:
                        try:
                            datetime.strptime(v, fmt)
                            date_count += 1
                            break
                        except ValueError:
                            pass

            total = len(values)
            if numeric_count / total > 0.8:
                col_types[col] = "numeric"
            elif date_count / total > 0.5:
                col_types[col] = "date"
            elif len(set(str(v)[:50] for v in values)) / total < 0.3:
                col_types[col] = "category"
            else:
                col_types[col] = "text"

        structure["tables_analysis"].append({
            "sheet_name": sheet.get("sheet_name", ""),
            "row_count": sheet.get("row_count", 0),
            "column_count": len(columns),
            "column_types": col_types,
            "numeric_columns": [c for c, t in col_types.items() if t == "numeric"],
            "date_columns": [c for c, t in col_types.items() if t == "date"],
            "category_columns": [c for c, t in col_types.items() if t == "category"],
        })

    # 分析文本
    para_count = data.get("paragraph_count", 0)
    page_count = data.get("page_count", 0)
    if para_count > 0 or page_count > 0:
        structure["text_analysis"] = {
            "paragraph_count": para_count,
            "page_count": page_count,
            "table_count": data.get("table_count", 0),
        }

    return json.dumps(structure, ensure_ascii=False)


def _resolve_path(file_path: str) -> str:
    """将相对路径转为绝对路径"""
    from app.tools.storage_tools import process_file_key
    return process_file_key(file_path)
```

- [ ] **Step 2: 语法验证**

```bash
python -m py_compile app/tools/file_tools.py && echo "OK" || echo "FAIL"
```

- [ ] **Step 3: 提交**

```bash
git add app/tools/file_tools.py
git commit -m "feat: add file_tools.py - Excel/CSV/DOCX/PDF parsing tools"
```

---

### Task 3.4: 创建 analysis_tools.py（数据分析工具）

**Files:**
- Create: `app/tools/analysis_tools.py`

- [ ] **Step 1: 创建 `app/tools/analysis_tools.py`**

```python
"""
通用数据分析工具

提供统计分析、异常检测、趋势分析、排名、相关性、
文本摘要、对比分析和分类等能力。
"""
import json
import math
import logging
from collections import Counter
from strands import tool


# ============================================================
# 辅助函数
# ============================================================

def _parse_input(data_json: str) -> dict:
    """解析 JSON 输入"""
    if isinstance(data_json, dict):
        return data_json
    return json.loads(data_json)


def _extract_column(data: dict, column: str) -> list:
    """从已解析数据中提取指定列的数值列表"""
    values = []
    for sheet in data.get("sheets", []):
        columns = sheet.get("columns", [])
        rows = sheet.get("rows", [])
        if column not in columns:
            continue
        idx = columns.index(column)
        for row in rows:
            if idx < len(row) and row[idx] is not None:
                try:
                    values.append(float(row[idx]))
                except (ValueError, TypeError):
                    pass
    return values


def _extract_series(data: dict, x_col: str, y_col: str) -> tuple:
    """提取两个列的数据序列"""
    xs, ys = [], []
    for sheet in data.get("sheets", []):
        columns = sheet.get("columns", [])
        rows = sheet.get("rows", [])
        if x_col not in columns or y_col not in columns:
            continue
        xi = columns.index(x_col)
        yi = columns.index(y_col)
        for row in rows:
            if xi < len(row) and yi < len(row):
                try:
                    ys.append(float(row[yi]))
                    xs.append(row[xi])
                except (ValueError, TypeError):
                    pass
    return xs, ys


# ============================================================
# 分析工具
# ============================================================

@tool
def statistical_summary(data_json: str, columns: str = "") -> str:
    """
    对指定列执行统计摘要：均值、中位数、标准差、最大/最小值、四分位数。

    参数:
        data_json: parse_* 输出的 JSON
        columns:   要分析的列名，逗号分隔。留空则分析所有数值列。
    返回:
        JSON 格式的统计结果
    """
    data = _parse_input(data_json)
    target_cols = [c.strip() for c in columns.split(",") if c.strip()] if columns else None

    # 自动发现数值列
    all_numeric = set()
    for sheet in data.get("sheets", []):
        for col in sheet.get("columns", []):
            vals = _extract_column(data, col)
            if vals:
                all_numeric.add(col)

    if target_cols is None:
        target_cols = list(all_numeric)
    else:
        target_cols = [c for c in target_cols if c in all_numeric]

    results = {}
    for col in target_cols:
        vals = sorted(_extract_column(data, col))
        if not vals:
            results[col] = {"error": "无有效数值"}
            continue

        n = len(vals)
        mean = sum(vals) / n
        median = vals[n // 2] if n % 2 == 1 else (vals[n // 2 - 1] + vals[n // 2]) / 2
        variance = sum((v - mean) ** 2 for v in vals) / n
        std = math.sqrt(variance)
        q1 = vals[n // 4]
        q3 = vals[3 * n // 4]

        results[col] = {
            "count": n,
            "mean": round(mean, 2),
            "median": round(median, 2),
            "std": round(std, 2),
            "min": round(vals[0], 2),
            "max": round(vals[-1], 2),
            "q1": round(q1, 2),
            "q3": round(q3, 2),
            "range": round(vals[-1] - vals[0], 2),
        }

    insights = []
    for col, r in results.items():
        if "error" in r:
            continue
        if r["std"] / (abs(r["mean"]) + 0.001) > 0.5:
            insights.append(f"{col} 数据波动较大（标准差={r['std']}），建议关注离群值")
        if r["max"] > r["mean"] + 3 * r["std"]:
            insights.append(f"{col} 存在极端最大值（{r['max']}），可考虑异常检测")

    return json.dumps({
        "method": "statistical_summary",
        "result": results,
        "insights": insights,
    }, ensure_ascii=False)


@tool
def anomaly_detection(data_json: str, column: str, threshold_sigma: float = 2.0) -> str:
    """
    基于 Z-score 方法检测指定列的异常值。

    参数:
        data_json:        parse_* 输出的 JSON
        column:           要检测的列名
        threshold_sigma:  Z-score 阈值（默认 2.0，即偏离均值 2 个标准差以上视为异常）
    返回:
        JSON 格式的异常检测结果
    """
    data = _parse_input(data_json)
    all_data = []
    for sheet in data.get("sheets", []):
        columns = sheet.get("columns", [])
        rows = sheet.get("rows", [])
        if column not in columns:
            continue
        idx = columns.index(column)
        for row in rows:
            if idx < len(row) and row[idx] is not None:
                try:
                    all_data.append({
                        "value": float(row[idx]),
                        "row": {c: row[ci] if ci < len(row) else None for ci, c in enumerate(columns)},
                    })
                except (ValueError, TypeError):
                    pass

    if not all_data:
        return json.dumps({"error": f"列 '{column}' 无有效数值"}, ensure_ascii=False)

    values = [d["value"] for d in all_data]
    n = len(values)
    mean = sum(values) / n
    std = math.sqrt(sum((v - mean) ** 2 for v in values) / n)

    if std == 0:
        return json.dumps({
            "method": "anomaly_detection",
            "column": column,
            "total_points": n,
            "anomalies": [],
            "insights": [f"{column} 所有值均相同（{mean}），无异常"],
        }, ensure_ascii=False)

    anomalies = []
    for d in all_data:
        z = abs(d["value"] - mean) / std
        if z > threshold_sigma:
            anomalies.append({
                "value": round(d["value"], 2),
                "z_score": round(z, 2),
                "deviation": round(d["value"] - mean, 2),
                "context": d["row"],
            })

    return json.dumps({
        "method": "anomaly_detection",
        "column": column,
        "total_points": n,
        "mean": round(mean, 2),
        "std": round(std, 2),
        "threshold_sigma": threshold_sigma,
        "anomaly_count": len(anomalies),
        "anomalies": anomalies,
        "insights": [
            f"检测到 {len(anomalies)} 个异常值（共 {n} 个数据点）",
            f"均值为 {mean:.2f}，标准差为 {std:.2f}",
        ],
    }, ensure_ascii=False)


@tool
def trend_analysis(data_json: str, time_col: str, value_col: str) -> str:
    """
    分析数值列随时间的变化趋势。

    参数:
        data_json:  parse_* 输出的 JSON
        time_col:   时间列名
        value_col:  数值列名
    返回:
        JSON 格式的趋势分析结果
    """
    data = _parse_input(data_json)
    xs, ys = _extract_series(data, time_col, value_col)
    if len(ys) < 2:
        return json.dumps({"error": "数据点不足（需至少 2 个点）"}, ensure_ascii=False)

    # 简单线性回归
    n = len(ys)
    x_idx = list(range(n))
    x_mean = (n - 1) / 2
    y_mean = sum(ys) / n
    numerator = sum((x_idx[i] - x_mean) * (ys[i] - y_mean) for i in range(n))
    denominator = sum((x_idx[i] - x_mean) ** 2 for i in range(n))
    slope = numerator / denominator if denominator != 0 else 0

    # 判断趋势
    if slope > 0.01 * abs(y_mean) if y_mean != 0 else slope > 0.01:
        direction = "上升"
    elif slope < -0.01 * abs(y_mean) if y_mean != 0 else slope < -0.01:
        direction = "下降"
    else:
        direction = "平稳"

    # 找拐点（简单方法：前后斜率变化）
    inflection_points = []
    for i in range(1, n - 1):
        pre = ys[i] - ys[i - 1]
        post = ys[i + 1] - ys[i]
        if pre * post < 0:
            inflection_points.append({"index": i, "time": str(xs[i]), "value": round(ys[i], 2)})

    return json.dumps({
        "method": "trend_analysis",
        "value_column": value_col,
        "time_column": time_col,
        "data_points": n,
        "first_value": round(ys[0], 2),
        "last_value": round(ys[-1], 2),
        "change": round(ys[-1] - ys[0], 2),
        "change_percent": round((ys[-1] - ys[0]) / (abs(ys[0]) + 0.001) * 100, 1),
        "direction": direction,
        "slope": round(slope, 4),
        "inflection_points": inflection_points,
        "insights": [
            f"整体趋势: {direction}（变化幅度 {round((ys[-1] - ys[0]) / (abs(ys[0]) + 0.001) * 100, 1)}%）",
            f"发现 {len(inflection_points)} 个趋势拐点",
        ],
    }, ensure_ascii=False)


@tool
def ranking(data_json: str, column: str, top_n: int = 10) -> str:
    """
    对指定列排序，返回 Top N 和 Bottom N。

    参数:
        data_json: parse_* 输出的 JSON
        column:    排序列名
        top_n:     返回前 N 和后 N 名（默认 10）
    返回:
        JSON 格式的排名结果
    """
    data = _parse_input(data_json)
    all_rows = []
    for sheet in data.get("sheets", []):
        columns = sheet.get("columns", [])
        rows = sheet.get("rows", [])
        if column not in columns:
            continue
        idx = columns.index(column)
        for row in rows:
            if idx < len(row) and row[idx] is not None:
                try:
                    all_rows.append({
                        "value": float(row[idx]),
                        "row": {c: row[ci] if ci < len(row) else None for ci, c in enumerate(columns)},
                    })
                except (ValueError, TypeError):
                    pass

    if not all_rows:
        return json.dumps({"error": f"列 '{column}' 无有效数值"}, ensure_ascii=False)

    sorted_rows = sorted(all_rows, key=lambda x: x["value"], reverse=True)
    n = min(top_n, len(sorted_rows))

    return json.dumps({
        "method": "ranking",
        "column": column,
        "total_items": len(all_rows),
        "top": [{"rank": i + 1, "value": round(r["value"], 2), "context": r["row"]}
                for i, r in enumerate(sorted_rows[:n])],
        "bottom": [{"rank": len(sorted_rows) - i, "value": round(r["value"], 2), "context": r["row"]}
                   for i, r in enumerate(reversed(sorted_rows[-n:]))],
    }, ensure_ascii=False, default=str)


@tool
def correlation(data_json: str, col_a: str, col_b: str) -> str:
    """
    计算两列数值之间的皮尔逊相关系数。

    参数:
        data_json: parse_* 输出的 JSON
        col_a:     第一列名
        col_b:     第二列名
    返回:
        JSON 格式的相关性结果
    """
    data = _parse_input(data_json)
    pairs = []
    for sheet in data.get("sheets", []):
        columns = sheet.get("columns", [])
        if col_a not in columns or col_b not in columns:
            continue
        ai = columns.index(col_a)
        bi = columns.index(col_b)
        for row in sheet.get("rows", []):
            if ai < len(row) and bi < len(row):
                try:
                    a = float(row[ai])
                    b = float(row[bi])
                    pairs.append((a, b))
                except (ValueError, TypeError):
                    pass

    if len(pairs) < 3:
        return json.dumps({"error": "有效数据对不足（需至少 3 对）"}, ensure_ascii=False)

    n = len(pairs)
    mean_a = sum(p[0] for p in pairs) / n
    mean_b = sum(p[1] for p in pairs) / n
    std_a = math.sqrt(sum((p[0] - mean_a) ** 2 for p in pairs) / n)
    std_b = math.sqrt(sum((p[1] - mean_b) ** 2 for p in pairs) / n)

    if std_a == 0 or std_b == 0:
        return json.dumps({"error": "某列方差为 0，无法计算相关性"}, ensure_ascii=False)

    cov = sum((p[0] - mean_a) * (p[1] - mean_b) for p in pairs) / n
    r = cov / (std_a * std_b)

    if abs(r) > 0.7:
        strength = "强" if abs(r) > 0.9 else "中等偏强"
    elif abs(r) > 0.4:
        strength = "中等"
    elif abs(r) > 0.2:
        strength = "弱"
    else:
        strength = "极弱或无"

    return json.dumps({
        "method": "correlation",
        "col_a": col_a,
        "col_b": col_b,
        "sample_size": n,
        "coefficient": round(r, 4),
        "strength": strength,
        "direction": "正相关" if r > 0 else "负相关",
        "insights": [
            f"{col_a} 与 {col_b} 呈{strength}{'正' if r > 0 else '负'}相关（r={r:.4f}）",
        ],
    }, ensure_ascii=False)


@tool
def text_summary(text_json: str, max_length: int = 500) -> str:
    """
    对文档文本提取关键要点（基于 LLM 调用时由 Agent 自行归纳；
    本工具提供文本统计和关键词频率，辅助归纳）。

    参数:
        text_json:  parse_docx / parse_pdf 输出的 JSON
        max_length: 最长返回字符数
    返回:
        文本分析结果 JSON
    """
    data = _parse_input(text_json)

    full_text = ""
    if "full_text" in data:
        full_text = data["full_text"]
    else:
        paragraphs = data.get("paragraphs", [])
        full_text = " ".join(p.get("text", "") for p in paragraphs)

    if not full_text:
        return json.dumps({"error": "无文本内容"}, ensure_ascii=False)

    # 词频统计（简单中文按字符、英文按词）
    words = full_text.replace("\n", " ").replace("\r", " ")
    # 简单分词（按标点 + 空格）
    import re
    tokens = [t for t in re.split(r'[，。！？；、\s,.!?;:]+', words) if len(t) >= 2]
    word_freq = Counter(tokens).most_common(30)

    return json.dumps({
        "method": "text_summary",
        "total_chars": len(full_text),
        "total_paragraphs": data.get("paragraph_count", 0),
        "total_tables": data.get("table_count", 0),
        "truncated": len(full_text) > max_length,
        "text_preview": full_text[:max_length],
        "top_keywords": [{"word": w, "count": c} for w, c in word_freq],
        "insights": [
            f"文档共 {len(full_text)} 字符，{data.get('paragraph_count', 0)} 段",
        ],
    }, ensure_ascii=False)


@tool
def comparison(data_a_json: str, data_b_json: str, key_column: str) -> str:
    """
    对比两个数据集，按 key_column 匹配并找出差异。

    参数:
        data_a_json: 数据集 A 的 parsed JSON
        data_b_json: 数据集 B 的 parsed JSON
        key_column:  用于匹配的键列
    返回:
        JSON 格式的对比结果
    """
    data_a = _parse_input(data_a_json)
    data_b = _parse_input(data_b_json)

    def build_index(d, key):
        idx = {}
        for sheet in d.get("sheets", []):
            columns = sheet.get("columns", [])
            if key not in columns:
                continue
            ki = columns.index(key)
            for row in sheet.get("rows", []):
                if ki < len(row):
                    idx[str(row[ki])] = row
        return idx

    idx_a = build_index(data_a, key_column)
    idx_b = build_index(data_b, key_column)

    keys_a = set(idx_a.keys())
    keys_b = set(idx_b.keys())
    common = keys_a & keys_b
    only_a = keys_a - keys_b
    only_b = keys_b - keys_a

    return json.dumps({
        "method": "comparison",
        "key_column": key_column,
        "total_a": len(keys_a),
        "total_b": len(keys_b),
        "common_count": len(common),
        "only_in_a": list(only_a)[:20],
        "only_in_b": list(only_b)[:20],
        "insights": [
            f"共同项: {len(common)}，仅在 A: {len(only_a)}，仅在 B: {len(only_b)}",
            f"匹配率: {round(len(common) / max(len(keys_a), len(keys_b)) * 100, 1) if max(len(keys_a), len(keys_b)) > 0 else 0}%",
        ],
    }, ensure_ascii=False)


@tool
def classification(text_json: str, categories: str = "") -> str:
    """
    对文本段落按指定类别分类（通过 LLM 推理；
    本工具返回文本块的预处理结果供 Agent 进一步分类）。

    参数:
        text_json:  parse_docx / parse_pdf 输出的 JSON
        categories: 分类类别，逗号分隔。留空则自动归纳。
    返回:
        预处理后的文本分段 JSON
    """
    data = _parse_input(text_json)
    paragraphs = data.get("paragraphs", [])
    if not paragraphs:
        return json.dumps({"error": "无段落可分类"}, ensure_ascii=False)

    segments = []
    for i, p in enumerate(paragraphs[:50]):  # 限制 50 段
        text = p.get("text", "").strip()
        if len(text) > 20:
            segments.append({
                "index": i,
                "text": text[:300],  # 每段截取 300 字符
                "style": p.get("style", ""),
            })

    cat_list = [c.strip() for c in categories.split(",") if c.strip()] if categories else []
    return json.dumps({
        "method": "classification",
        "segment_count": len(segments),
        "provided_categories": cat_list,
        "segments": segments,
    }, ensure_ascii=False)
```

- [ ] **Step 2: 语法验证**

```bash
python -m py_compile app/tools/analysis_tools.py && echo "OK" || echo "FAIL"
```

- [ ] **Step 3: 提交**

```bash
git add app/tools/analysis_tools.py
git commit -m "feat: add analysis_tools.py - 8 generic analysis tools"
```

---

### Task 3.5: 创建 viz_tools.py（可视化工具）

**Files:**
- Create: `app/tools/viz_tools.py`

- [ ] **Step 1: 创建 `app/tools/viz_tools.py`**

```python
"""
可视化工具

提供图表配置生成、HTML 表格渲染、报告模板填充等能力。
"""
import json
import logging
from strands import tool


@tool
def render_line_chart(data_json: str, title: str, x_label: str, y_label: str) -> str:
    """
    生成 Chart.js 折线图配置 JSON（供报告模板插入）。

    参数:
        data_json: 格式 {"labels": [...], "datasets": [{"label": "...", "data": [...]}, ...]}
        title:     图表标题
        x_label:   X 轴标签
        y_label:   Y 轴标签
    返回:
        Chart.js 配置 JSON 字符串
    """
    try:
        chart_data = json.loads(data_json)
    except json.JSONDecodeError:
        return json.dumps({"error": "data_json 不是有效 JSON"})

    config = {
        "type": "line",
        "data": chart_data,
        "options": {
            "responsive": True,
            "maintainAspectRatio": False,
            "plugins": {
                "title": {"display": True, "text": title, "font": {"size": 16}},
                "tooltip": {"mode": "index", "intersect": False},
            },
            "scales": {
                "x": {"title": {"display": True, "text": x_label}},
                "y": {"title": {"display": True, "text": y_label}, "beginAtZero": False},
            },
        },
    }
    return json.dumps(config, ensure_ascii=False)


@tool
def render_bar_chart(data_json: str, title: str, x_label: str, y_label: str) -> str:
    """
    生成 Chart.js 柱状图配置 JSON。

    参数同 render_line_chart。
    """
    try:
        chart_data = json.loads(data_json)
    except json.JSONDecodeError:
        return json.dumps({"error": "data_json 不是有效 JSON"})

    config = {
        "type": "bar",
        "data": chart_data,
        "options": {
            "responsive": True,
            "maintainAspectRatio": False,
            "plugins": {
                "title": {"display": True, "text": title, "font": {"size": 16}},
                "tooltip": {"mode": "index", "intersect": False},
            },
            "scales": {
                "x": {"title": {"display": True, "text": x_label}},
                "y": {"title": {"display": True, "text": y_label}, "beginAtZero": True},
            },
        },
    }
    return json.dumps(config, ensure_ascii=False)


@tool
def render_radar_chart(data_json: str, title: str) -> str:
    """
    生成 Chart.js 雷达图配置 JSON。

    参数:
        data_json: 格式 {"labels": [...], "datasets": [{"label": "...", "data": [...]}, ...]}
        title:     图表标题
    """
    try:
        chart_data = json.loads(data_json)
    except json.JSONDecodeError:
        return json.dumps({"error": "data_json 不是有效 JSON"})

    config = {
        "type": "radar",
        "data": chart_data,
        "options": {
            "responsive": True,
            "maintainAspectRatio": False,
            "plugins": {
                "title": {"display": True, "text": title, "font": {"size": 16}},
            },
        },
    }
    return json.dumps(config, ensure_ascii=False)


@tool
def render_table(data_json: str, title: str) -> str:
    """
    生成 HTML 表格片段。

    参数:
        data_json: 格式 {"columns": [...], "rows": [[...], ...]}
        title:     表格标题
    返回:
        HTML 表格字符串
    """
    try:
        table_data = json.loads(data_json)
    except json.JSONDecodeError:
        return "<p style='color:red;'>错误：data_json 不是有效 JSON</p>"

    columns = table_data.get("columns", [])
    rows = table_data.get("rows", [])

    html = f"<h3>{title}</h3>\n"
    html += "<table style='width:100%;border-collapse:collapse;margin:16px 0;'>\n"
    html += "<thead><tr>"
    for col in columns:
        html += f"<th style='border:1px solid #ddd;padding:8px;background:#f5f5f5;text-align:left;'>{col}</th>"
    html += "</tr></thead>\n<tbody>"

    for i, row in enumerate(rows):
        bg = "#fafafa" if i % 2 == 0 else "#fff"
        html += f"<tr style='background:{bg};'>"
        for cell in row:
            val = str(cell) if cell is not None else ""
            html += f"<td style='border:1px solid #ddd;padding:8px;'>{val}</td>"
        html += "</tr>\n"

    html += "</tbody></table>"
    return html


@tool
def render_summary_card(metrics_json: str) -> str:
    """
    生成数据摘要卡片 HTML 片段。

    参数:
        metrics_json: 格式 [{"label": "总销售额", "value": "12.3万", "trend": "up"}, ...]
    返回:
        HTML 卡片片段
    """
    try:
        metrics = json.loads(metrics_json)
    except json.JSONDecodeError:
        return "<p style='color:red;'>错误：metrics_json 不是有效 JSON</p>"

    cards = ""
    trend_icons = {"up": "▲", "down": "▼", "flat": "—"}
    trend_colors = {"up": "#22c55e", "down": "#ef4444", "flat": "#6b7280"}

    for m in metrics:
        trend = m.get("trend", "flat")
        icon = trend_icons.get(trend, "")
        color = trend_colors.get(trend, "#6b7280")
        cards += f"""
        <div style="flex:1;min-width:180px;padding:20px;background:#fff;
                    border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.1);text-align:center;">
            <div style="font-size:14px;color:#6b7280;margin-bottom:8px;">{m.get('label', '')}</div>
            <div style="font-size:28px;font-weight:bold;color:#1f2937;">
                {m.get('value', '')}
                <span style="font-size:16px;color:{color};">{icon}</span>
            </div>
        </div>"""

    return f"<div style='display:flex;gap:16px;flex-wrap:wrap;margin:24px 0;'>{cards}</div>"


@tool
def apply_report_template(template_id: str, analysis_results_json: str) -> str:
    """
    选择并返回报告模板的 HTML 骨架（带占位标记），
    供 Visualizer Agent 填充实际数据后调用 write_local_file_html 写入。

    参数:
        template_id:           报告模板 ID（executive_dashboard / minimal_report）
        analysis_results_json: 分析结果汇总 JSON
    返回:
        模板选择建议 + 模板骨架 HTML
    """
    # 模板选择逻辑（简化版 — 实际模板文件在 report_templates/ 目录下）
    if template_id == "executive_dashboard":
        template_hint = "executive_dashboard"
    else:
        template_hint = "minimal_report"

    return json.dumps({
        "template": template_hint,
        "message": f"请读取 report_templates/{template_hint}.html 模板文件，"
                   f"将以下分析结果填入模板占位区域，包括图表 <canvas> 元素和表格区域。"
                   f"使用 render_line_chart 等工具的输出来填充图表配置。",
    }, ensure_ascii=False)


@tool
def self_review(html_content: str) -> str:
    """
    对生成的 HTML 报告进行质量自检。

    检查项:
    1. 完整的 HTML5 结构
    2. Chart.js CDN 引用
    3. Canvas 元素存在性
    4. 响应式 viewport
    5. 明显的数据占位符残留

    参数:
        html_content: HTML 报告内容
    返回:
        审核结果 JSON
    """
    checks = []
    issues = []

    checks.append({"check": "DOCTYPE", "pass": "<!DOCTYPE html>" in html_content[:100]})
    checks.append({"check": "charset", "pass": 'charset="UTF-8"' in html_content or "charset='UTF-8'" in html_content})
    checks.append({"check": "viewport", "pass": "viewport" in html_content.lower()})
    checks.append({"check": "chartjs_cdn", "pass": "chart.js" in html_content.lower()})
    checks.append({"check": "body_tag", "pass": "<body" in html_content.lower() and "</body>" in html_content.lower()})

    # 检查是否有明显的占位符残留
    placeholders = ["{{", "}}", "TODO", "FIXME", "PLACEHOLDER"]
    for ph in placeholders:
        if ph in html_content:
            issues.append(f"发现未替换的占位符: {ph}")

    all_pass = all(c["pass"] for c in checks) and len(issues) == 0

    return json.dumps({
        "overall": "pass" if all_pass else "needs_fix",
        "checks": checks,
        "issues": issues,
    }, ensure_ascii=False)
```

- [ ] **Step 2: 语法验证**

```bash
python -m py_compile app/tools/viz_tools.py && echo "OK" || echo "FAIL"
```

- [ ] **Step 3: 提交**

```bash
git add app/tools/viz_tools.py
git commit -m "feat: add viz_tools.py - chart rendering and report template tools"
```

---

## 阶段 4：Prompt 层 — 创建 4 个 Agent System Prompt

### Task 4.1: 创建 coordinator_prompt.py

**Files:**
- Create: `app/prompt/coordinator_prompt.py`

- [ ] **Step 1: 创建文件**

```python
coordinator_prompt = """
你是一个数据分析项目协调者(Coordinator Agent)。你的职责是接收用户的分析需求，调度专家 Agent 完成任务，最终交付高质量的分析报告。

## 你的团队

你可以调用以下 3 个专家 Agent：

1. **fetcher_agent** — 数据获取专家
   - 能力：解析用户上传的文件（Excel / CSV / Word / PDF），提取结构化数据
   - 工具：parse_excel, parse_csv, parse_docx, parse_pdf, detect_structure

2. **analyzer_agent** — 数据分析专家
   - 能力：对结构化数据执行统计分析、异常检测、趋势分析、排名、相关性分析、文本摘要、对比分析、分类
   - 工具：statistical_summary, anomaly_detection, trend_analysis, ranking, correlation, text_summary, comparison, classification

3. **visualizer_agent** — 可视化专家
   - 能力：将分析结果渲染为 HTML 报告，包含交互式图表、数据表格、摘要卡片
   - 工具：render_line_chart, render_bar_chart, render_radar_chart, render_table, render_summary_card, apply_report_template, write_local_file_html, self_review

## 工作流程

### 第一步：理解需求
- 如果用户选择了分析模板，直接加载模板配置（从模板 ID 获取 methods 列表和 report 配置）
- 如果用户用自然语言描述需求，推理出应该执行哪些分析方法
- 确认需要分析的文件列表

### 第二步：获取数据
调用 fetcher_agent，传入文件路径列表。fetcher_agent 会逐个解析文件并返回统一格式的结构化数据。
- 如果是单个文件，fetcher 返回一份数据
- 如果是多个文件，fetcher 分别解析后，你需要判断文件之间的关系并规划后续分析路径

### 第三步：分析数据
调用 analyzer_agent，传入 Fetcher 输出的结构化数据和需要执行的分析方法列表。
analyzer_agent 会依次执行每项分析并返回结果。
- 注意：如果执行失败，可以重试或跳过该项分析
- 多文件场景：对每个文件分别调用 analyzer，如有对比需求再单独调用 comparison

### 第四步：生成报告
调用 visualizer_agent，传入分析结果汇总和报告模板 ID。
visualizer_agent 会生成包含图表的完整 HTML 报告。
- 报告模板 ID 从模板配置中获取
- visualizer_agent 完成后会自动自检报告质量

### 第五步：交付
确认报告已写入本地存储，总结分析结果的关键发现，告知用户报告位置或输出报告摘要。

## 处理用户反馈
如果用户对报告不满意并提出反馈（如"缺了结构分析"、"增加对比"等），你需要：
1. 分析反馈，判断缺少的是什么
2. 直接调用 analyzer_agent 追加分析（跳过 fetcher，数据已有）
3. 调用 visualizer_agent 重新生成报告
4. 无须重新解析文件和修改模板

## 重要规则
- **按顺序执行**：Fetcher → Analyzer → Visualizer
- **错误处理**：某个方法失败时，尝试简化参数重试一次，仍失败则跳过并记录
- **进度报告**：每一步完成后返回当前进度
- **多文件智能处理**：根据文件类型和内容判断它们之间的关系（同质对比/异质综合）
- **最终确认**：总结执行结果，列出生成的报告路径
"""
```

- [ ] **Step 2: 语法验证 + 提交**

```bash
python -m py_compile app/prompt/coordinator_prompt.py && echo "OK" || echo "FAIL"
git add app/prompt/coordinator_prompt.py
git commit -m "feat: add coordinator_prompt.py - generic coordinator system prompt"
```

---

### Task 4.2: 创建 fetcher_prompt.py

**Files:**
- Create: `app/prompt/fetcher_prompt.py`

- [ ] **Step 1: 创建文件**

```python
fetcher_prompt = """
你是一个数据获取专家(Fetcher Agent)。你负责解析用户上传的文件，提取结构化数据供后续分析使用。

## 你的工具

- **parse_excel** — 解析 Excel 文件（xlsx/xls），输出所有工作表的表头和数据行
- **parse_csv** — 解析 CSV 文件，支持自定义分隔符
- **parse_docx** — 解析 Word 文档（docx），提取段落文本和嵌入表格
- **parse_pdf** — 解析 PDF 文件，提取每页文本
- **detect_structure** — 分析已解析数据的结构：识别每列的数据类型（数值/日期/分类/文本）

## 工作流程

### 1. 识别文件类型
根据文件扩展名确定解析方式：
- xlsx / xls → parse_excel
- csv → parse_csv
- docx → parse_docx
- pdf → parse_pdf

### 2. 逐个解析
对每个文件调用对应的解析工具。如果文件有多个工作表（Excel），解析所有工作表。

### 3. 结构识别
调用 detect_structure 分析每个文件的列类型，帮助后续分析确定哪些列可以做统计分析、哪些是分类维度。

### 4. 输出统一格式
所有文件解析完成后，汇总成以下格式返回给 Coordinator：

{
  "files": [
    {
      "filename": "原始文件名",
      "file_type": "xlsx/csv/docx/pdf",
      "parsed": { parse_* 的输出 },
      "structure": { detect_structure 的输出 }
    }
  ],
  "summary": "共 N 个文件，其中 M 个表格文件，K 个文档文件"
}

## 重要提醒
- 遇到无法解析的文件，返回明确的错误信息而不是崩溃
- Excel 文件默认只解析第一个工作表，除非 Coordinator 指定了工作表名
- 大文件只解析前 1000 行进行预览
- CSV 文件先尝试 utf-8 编码，失败则尝试 gbk
"""
```

- [ ] **Step 2: 语法验证 + 提交**

```bash
python -m py_compile app/prompt/fetcher_prompt.py && echo "OK" || echo "FAIL"
git add app/prompt/fetcher_prompt.py
git commit -m "feat: add fetcher_prompt.py - generic file parsing prompt"
```

---

### Task 4.3: 创建 analyzer_prompt.py

**Files:**
- Create: `app/prompt/analyzer_prompt.py`

- [ ] **Step 1: 创建文件**

```python
analyzer_prompt = """
你是一个数据分析专家(Analyzer Agent)。你对结构化数据执行深度分析，输出量化结论和洞察。

## 你的工具

- **statistical_summary** — 统计摘要：均值、中位数、标准差、四分位数、最大/最小值
- **anomaly_detection** — 异常检测：基于 Z-score 检测离群值
- **trend_analysis** — 趋势分析：计算变化方向、幅度、拐点
- **ranking** — 排名分析：Top N 和 Bottom N
- **correlation** — 相关性分析：两列数值的皮尔逊相关系数
- **text_summary** — 文本摘要：关键词频率、文本统计
- **comparison** — 对比分析：两个数据集的差异对比
- **classification** — 分类：文本段落按类别归类

## 工作流程

### 1. 接收数据和分析配置
Coordinator 会传入：
- Fetcher 输出的结构化数据
- 需要执行的分析方法列表（如 ["trend_analysis", "ranking"]）
- 可能包含 hints（如优先关注哪些列）

### 2. 逐项执行分析
对 methods 列表中的每一项，确定应该分析哪些列：
- trend_analysis: 需要时间列 + 数值列
- ranking: 需要数值列
- correlation: 需要两列数值
- anomaly_detection: 需要数值列
- text_summary: 需要文本数据
- comparison: 需要两个数据集 + 匹配键
- 根据 detect_structure 的结果自动选择最合适的列

### 3. 合并输出
所有分析完成后，汇总为统一的结果 JSON：
{
  "analyses": [
    {"method": "statistical_summary", "result": {...}},
    {"method": "trend_analysis", "result": {...}},
    ...
  ],
  "overall_insights": ["综合洞察1", "综合洞察2", ...]
}

## 分析与结论规范
- 每个分析结果必须包含 "insights" 字段，用自然语言总结关键发现
- 数值保留 2 位小数
- 如果数据不足以执行某项分析，返回明确的跳过原因
- 不要编造数据，所有结论必须来自工具的实际输出
"""
```

- [ ] **Step 2: 语法验证 + 提交**

```bash
python -m py_compile app/prompt/analyzer_prompt.py && echo "OK" || echo "FAIL"
git add app/prompt/analyzer_prompt.py
git commit -m "feat: add analyzer_prompt.py - generic data analysis prompt"
```

---

### Task 4.4: 创建 visualizer_prompt.py

**Files:**
- Create: `app/prompt/visualizer_prompt.py`

- [ ] **Step 1: 创建文件**

```python
visualizer_prompt = """
你是一个可视化专家(Visualizer Agent)。你将分析结果渲染为精美的 HTML 报告。

## 你的工具

图表渲染:
- **render_line_chart** — 生成 Chart.js 折线图配置
- **render_bar_chart** — 生成 Chart.js 柱状图配置
- **render_radar_chart** — 生成 Chart.js 雷达图配置

HTML 组件:
- **render_table** — 生成 HTML 表格
- **render_summary_card** — 生成数据摘要卡片
- **apply_report_template** — 获取报告模板建议

文件操作:
- **write_local_file_html** — 将 HTML 写入本地存储
- **self_review** — 自检报告质量

## 工作流程

### 1. 接收分析结果
Coordinator 会传入：
- Analyzer 输出的分析结果 JSON
- 报告模板 ID
- 报告标题

### 2. 处理分析结果
逐个处理 analysis_results，为每种分析类型选择合适的展示方式：

| 分析类型 | 推荐图表 | 推荐组件 |
|---------|---------|---------|
| statistical_summary | — | summary_card + table |
| anomaly_detection | — | table（高亮异常行） |
| trend_analysis | line_chart | — |
| ranking | bar_chart | table |
| correlation | — | summary_card + insights 文本 |
| text_summary | — | 格式化文本块 |
| comparison | bar_chart | table |
| classification | — | 分类列表 |

### 3. 生成报告 HTML
组装完整的 HTML 页面，结构如下：
1. 报告头部（标题、分析时间、文件信息）
2. 摘要卡片区（关键指标卡片）
3. 图表区（折线图、柱状图、雷达图等）
4. 表格区（异常表格、排名表格）
5. 洞察区（综合发现和建议）

### 4. HTML 技术规范
- 使用 HTML5 文档类型
- Chart.js CDN: https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js
- CSS 全部内联在 <style> 标签中
- 配色方案：主色 #1e40af，辅色 #3b82f6，背景 #f8fafc
- 响应式设计：使用 max-width: 1200px 居中容器
- Canvas 高度 350px
- 图表使用 DOMContentLoaded 事件初始化

### 5. 自检与写入
生成 HTML 后，先调用 self_review 检查质量。如果通过，调用 write_local_file_html 写入文件。
如果发现问题，修正后重新写入。

## 重要提醒
- 所有数据必须来自 Analyzer 的输出，不要编造
- 图表数据如果为空，显示友好的"暂无数据"提示
- 避免在报告中使用英文变量名和术语
- 报告标题、章节标题使用中文
"""
```

- [ ] **Step 2: 语法验证 + 提交**

```bash
python -m py_compile app/prompt/visualizer_prompt.py && echo "OK" || echo "FAIL"
git add app/prompt/visualizer_prompt.py
git commit -m "feat: add visualizer_prompt.py - generic visualization prompt"
```

---

## 阶段 5：Agent 层 — 创建 4 个 Agent 定义

### Task 5.1: 创建 coordinator_agent.py

**Files:**
- Create: `app/agents/coordinator_agent.py`

- [ ] **Step 1: 创建文件**

```python
from strands import Agent, tool
from app.agents.fetcher_agent import fetcher_agent
from app.agents.analyzer_agent import analyzer_agent
from app.agents.visualizer_agent import visualizer_agent
from app.models.LLM_model import ModelInstances
from app.prompt.coordinator_prompt import coordinator_prompt


coordinator = Agent(
    system_prompt=coordinator_prompt,
    model=ModelInstances.LEADER_MODEL,
    tools=[
        fetcher_agent,
        analyzer_agent,
        visualizer_agent,
    ],
)
```

- [ ] **Step 2: 语法验证 + 提交**

```bash
python -m py_compile app/agents/coordinator_agent.py && echo "OK" || echo "FAIL"
git add app/agents/coordinator_agent.py
git commit -m "feat: add coordinator_agent.py - 3-sub-agent orchestrator"
```

---

### Task 5.2: 创建 fetcher_agent.py

**Files:**
- Create: `app/agents/fetcher_agent.py`

- [ ] **Step 1: 创建文件**

```python
from strands import Agent, tool
from app.tools.file_tools import (
    parse_excel, parse_csv, parse_docx, parse_pdf, detect_structure,
)
from app.models.LLM_model import ModelInstances
from app.prompt.fetcher_prompt import fetcher_prompt


@tool
def fetcher_agent(query: str) -> str:
    """
    数据获取专家：解析用户上传的文件（Excel / CSV / Word / PDF），
    提取结构化数据并识别数据类型。

    Args:
        query: 文件路径列表和解析指令

    Returns:
        统一格式的结构化数据 JSON
    """
    formatted_query = (
        f"请解析以下文件，调用对应的 parse_* 工具提取结构化数据，"
        f"然后调用 detect_structure 分析每列的数据类型: {query}"
    )

    try:
        print("[Fetcher] 开始解析文件...")
        agent = Agent(
            system_prompt=fetcher_prompt,
            model=ModelInstances.LEADER_MODEL,
            tools=[
                parse_excel, parse_csv, parse_docx, parse_pdf, detect_structure,
            ],
        )
        response = agent(formatted_query)
        text_response = str(response)

        if len(text_response) > 0:
            return text_response

        return "错误：无法解析文件，请确认文件格式正确"
    except Exception as e:
        return f"数据获取出错: {str(e)}"
```

- [ ] **Step 2: 语法验证 + 提交**

```bash
python -m py_compile app/agents/fetcher_agent.py && echo "OK" || echo "FAIL"
git add app/agents/fetcher_agent.py
git commit -m "feat: add fetcher_agent.py - file parsing agent"
```

---

### Task 5.3: 创建 analyzer_agent.py

**Files:**
- Create: `app/agents/analyzer_agent.py`

- [ ] **Step 1: 创建文件**

```python
from strands import Agent, tool
from app.tools.analysis_tools import (
    statistical_summary, anomaly_detection, trend_analysis,
    ranking, correlation, text_summary, comparison, classification,
)
from app.models.LLM_model import ModelInstances
from app.prompt.analyzer_prompt import analyzer_prompt


@tool
def analyzer_agent(query: str) -> str:
    """
    数据分析专家：对结构化数据执行统计分析、异常检测、趋势分析等。

    Args:
        query: 结构化数据和分析方法列表

    Returns:
        分析结果 JSON
    """
    formatted_query = (
        f"请对以下数据执行分析。使用提供的工具逐项完成分析方法列表中的每一项，"
        f"最后汇总所有分析结果和综合洞察: {query}"
    )

    try:
        print("[Analyzer] 开始数据分析...")
        agent = Agent(
            system_prompt=analyzer_prompt,
            model=ModelInstances.LEADER_MODEL,
            tools=[
                statistical_summary, anomaly_detection, trend_analysis,
                ranking, correlation, text_summary, comparison, classification,
            ],
        )
        response = agent(formatted_query)
        text_response = str(response)

        if len(text_response) > 0:
            return text_response

        return "错误：无法完成数据分析"
    except Exception as e:
        return f"数据分析出错: {str(e)}"
```

- [ ] **Step 2: 语法验证 + 提交**

```bash
python -m py_compile app/agents/analyzer_agent.py && echo "OK" || echo "FAIL"
git add app/agents/analyzer_agent.py
git commit -m "feat: add analyzer_agent.py - data analysis agent"
```

---

### Task 5.4: 创建 visualizer_agent.py

**Files:**
- Create: `app/agents/visualizer_agent.py`

- [ ] **Step 1: 创建文件**

```python
from strands import Agent, tool
from app.tools.viz_tools import (
    render_line_chart, render_bar_chart, render_radar_chart,
    render_table, render_summary_card, apply_report_template, self_review,
)
from app.tools.storage_tools import write_local_file_html, read_local_file
from app.models.LLM_model import ModelInstances
from app.prompt.visualizer_prompt import visualizer_prompt


@tool
def visualizer_agent(query: str) -> str:
    """
    可视化专家：将分析结果渲染为 HTML 报告，包含交互式图表。

    Args:
        query: 分析结果汇总和报告模板 ID

    Returns:
        报告生成结果
    """
    formatted_query = (
        f"请根据以下分析结果和报告模板，生成完整的 HTML 可视化报告。"
        f"使用图表渲染工具创建图表配置，然后组装完整的 HTML 页面，"
        f"自检后写入本地存储: {query}"
    )

    try:
        print("[Visualizer] 开始生成报告...")
        agent = Agent(
            system_prompt=visualizer_prompt,
            model=ModelInstances.LEADER_MODEL,
            tools=[
                render_line_chart, render_bar_chart, render_radar_chart,
                render_table, render_summary_card, apply_report_template,
                write_local_file_html, read_local_file, self_review,
            ],
        )
        response = agent(formatted_query)
        text_response = str(response)

        if len(text_response) > 0:
            return text_response

        return "错误：无法生成报告"
    except Exception as e:
        return f"报告生成出错: {str(e)}"
```

- [ ] **Step 2: 语法验证 + 提交**

```bash
python -m py_compile app/agents/visualizer_agent.py && echo "OK" || echo "FAIL"
git add app/agents/visualizer_agent.py
git commit -m "feat: add visualizer_agent.py - report generation agent"
```

---

## 阶段 6：API 层 — 创建 7 个端点

### Task 6.1: 创建 upload.py（文件上传端点）

**Files:**
- Create: `app/api/upload.py`

- [ ] **Step 1: 创建文件**

```python
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
    # 校验扩展名
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED:
        raise HTTPException(400, f"不支持的文件类型 .{ext}，允许: {ALLOWED}")

    # 校验大小
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(400, f"文件过大（{len(content)} 字节），上限 {MAX_SIZE} 字节")

    # 存储
    session_id = uuid.uuid4().hex[:8]
    upload_id = uuid.uuid4().hex[:12]
    file_name = f"{upload_id}_{file.filename}"
    rel_path = f"uploads/{session_id}/{file_name}"
    abs_path = process_file_key(rel_path)

    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "wb") as f:
        f.write(content)

    # 记录元数据
    with LocalSession() as db:
        upload = Upload(
            id=upload_id,
            filename=file.filename,
            file_type=ext,
            file_size=len(content),
            file_path=rel_path,
            session_id=session_id,
        )
        db.add(upload)
        db.commit()

    return {
        "file_id": upload_id,
        "filename": file.filename,
        "file_type": ext,
        "file_size": len(content),
        "session_id": session_id,
    }
```

- [ ] **Step 2: 语法验证 + 提交**

```bash
python -m py_compile app/api/upload.py && echo "OK" || echo "FAIL"
git add app/api/upload.py
git commit -m "feat: add upload endpoint with validation and SQLite metadata"
```

---

### Task 6.2: 创建 tasks.py 和 reports.py

**Files:**
- Create: `app/api/tasks.py`
- Create: `app/api/reports.py`

- [ ] **Step 1: 创建 `app/api/tasks.py`**

```python
"""任务状态端点"""
from fastapi import APIRouter, HTTPException
from app.models.database import LocalSession, Task

router = APIRouter()


@router.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str):
    """查询分析任务状态"""
    with LocalSession() as db:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(404, "任务不存在")

        return {
            "task_id": task.id,
            "status": task.status,
            "progress": task.progress,
            "error_message": task.error_message,
            "created_at": task.created_at,
            "completed_at": task.completed_at,
        }


@router.get("/api/history")
async def list_history(page: int = 1, size: int = 20):
    """历史分析记录"""
    with LocalSession() as db:
        total = db.query(Task).count()
        tasks = (
            db.query(Task)
            .order_by(Task.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )
        return {
            "total": total,
            "page": page,
            "size": size,
            "items": [
                {
                    "task_id": t.id,
                    "status": t.status,
                    "template_id": t.template_id,
                    "nl_query": t.nl_query,
                    "created_at": t.created_at,
                    "completed_at": t.completed_at,
                }
                for t in tasks
            ],
        }
```

- [ ] **Step 2: 创建 `app/api/reports.py`**

```python
"""报告查询端点"""
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from app.models.database import LocalSession, Task, Report
from app.tools.storage_tools import process_file_key

router = APIRouter()


@router.get("/api/reports/{task_id}")
async def get_report(task_id: str):
    """获取分析报告 HTML"""
    with LocalSession() as db:
        report = db.query(Report).filter(Report.task_id == task_id).first()
        if not report:
            raise HTTPException(404, "报告不存在")

        abs_path = process_file_key(report.file_path)
        if not os.path.exists(abs_path):
            raise HTTPException(404, f"报告文件不存在: {abs_path}")

        with open(abs_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        return HTMLResponse(content=html_content)


@router.get("/api/reports/{task_id}/download")
async def download_report(task_id: str):
    """下载报告 ZIP"""
    with LocalSession() as db:
        report = db.query(Report).filter(Report.task_id == task_id).first()
        if not report:
            raise HTTPException(404, "报告不存在")

        abs_path = process_file_key(report.file_path)
        if not os.path.exists(abs_path):
            raise HTTPException(404, "报告文件不存在")

        return FileResponse(abs_path, filename=f"report_{task_id}.html")
```

- [ ] **Step 3: 语法验证 + 提交**

```bash
python -m py_compile app/api/tasks.py && python -m py_compile app/api/reports.py && echo "OK" || echo "FAIL"
git add app/api/tasks.py app/api/reports.py
git commit -m "feat: add tasks and reports API endpoints"
```

---

### Task 6.3: 重写 api.py（核心分析端点 + 模板端点）

**Files:**
- Modify: `app/api/api.py`

- [ ] **Step 1: 完全重写 `app/api/api.py`**

```python
"""核心 API 端点：发起分析、反馈、模板管理"""
import json
import asyncio
import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List

from app.models.database import LocalSession, Upload, Task, Report
from app.config.template_loader import get_template, list_templates

router = APIRouter()


# ---- 请求模型 ----

class AnalysisRequest(BaseModel):
    file_ids: List[str]
    template_id: Optional[str] = None
    nl_query: Optional[str] = None


class FeedbackRequest(BaseModel):
    satisfaction: str           # satisfied / partial / unsatisfied
    missing_items: List[str] = []  # 缺失的分析项
    description: Optional[str] = None


# ---- 端点 ----

@router.get("/")
async def root():
    return {"message": "Multi-Agent Data Analysis Platform", "version": "1.0.0"}


@router.get("/api/templates")
async def get_templates():
    """获取可用分析模板列表"""
    return {"templates": list_templates()}


@router.post("/api/analysis/run")
async def run_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """发起分析任务（异步后台执行）"""
    if not request.file_ids:
        raise HTTPException(400, "至少需要上传一个文件")
    if not request.template_id and not request.nl_query:
        raise HTTPException(400, "请选择分析模板或输入分析需求")

    # 验证文件存在
    with LocalSession() as db:
        uploads = db.query(Upload).filter(Upload.id.in_(request.file_ids)).all()
        if len(uploads) != len(request.file_ids):
            raise HTTPException(404, "部分文件未找到")
        file_paths = [u.file_path for u in uploads]
        file_names = [u.filename for u in uploads]
        task_id = Task(id=None).id  # 触发 default 生成
        task = Task(
            id=task_id,
            upload_ids=json.dumps(request.file_ids),
            template_id=request.template_id,
            nl_query=request.nl_query,
            status="pending",
            progress="任务已创建",
        )
        db.add(task)
        db.commit()

    # 后台异步执行
    background_tasks.add_task(
        _execute_analysis,
        task_id=task_id,
        file_paths=file_paths,
        file_names=file_names,
        template_id=request.template_id,
        nl_query=request.nl_query,
    )

    return {"task_id": task_id, "status": "pending"}


@router.post("/api/feedback/{task_id}")
async def submit_feedback(task_id: str, request: FeedbackRequest):
    """提交报告反馈，触发重跑"""
    with LocalSession() as db:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(404, "任务不存在")
        analysis_config = json.loads(task.analysis_config or "{}")
        upload_ids = json.loads(task.upload_ids or "[]")

        uploads = db.query(Upload).filter(Upload.id.in_(upload_ids)).all()
        file_paths = [u.file_path for u in uploads]
        file_names = [u.filename for u in uploads]

    # 创建新任务（基于反馈）
    new_task_id = Task(id=None).id
    with LocalSession() as db:
        new_task = Task(
            id=new_task_id,
            upload_ids=json.dumps(upload_ids),
            template_id=task.template_id,
            nl_query=f"用户反馈: {request.description or ''}，缺失: {request.missing_items}",
            status="pending",
            progress="基于反馈重新分析",
        )
        db.add(new_task)
        db.commit()

    import asyncio
    asyncio.create_task(
        _execute_analysis_with_feedback(
            task_id=new_task_id,
            file_paths=file_paths,
            file_names=file_names,
            original_config=analysis_config,
            feedback=request,
        )
    )

    return {"task_id": new_task_id, "status": "pending", "message": "已基于反馈创建新任务"}


# ---- 后台执行逻辑 ----

async def _execute_analysis(
    task_id: str,
    file_paths: List[str],
    file_names: List[str],
    template_id: Optional[str],
    nl_query: Optional[str],
):
    """后台异步执行分析流水线"""
    from app.agents.coordinator_agent import coordinator

    def update_status(status: str, progress: str):
        with LocalSession() as db:
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                task.status = status
                task.progress = progress
                if status in ("done", "failed"):
                    task.completed_at = datetime.now().isoformat(timespec="seconds")
                db.commit()

    try:
        update_status("parsing", "正在解析文件...")

        # 构建 Coordinator 的输入
        files_info = "\n".join(
            f"- {name} (路径: {path})" for name, path in zip(file_names, file_paths)
        )

        if template_id and not nl_query:
            template = get_template(template_id)
            if template:
                query = (
                    f"请按照以下模板配置执行分析:\n"
                    f"模板: {template['name']}\n"
                    f"分析方法: {template['analysis']['methods']}\n"
                    f"报告模板: {template['report']['template']}\n"
                    f"文件列表:\n{files_info}\n"
                )
            else:
                query = f"分析以下文件:\n{files_info}\n"
        else:
            query = f"用户需求: {nl_query}\n文件列表:\n{files_info}"

        update_status("analyzing", "正在执行分析...")
        response = await coordinator.invoke_async(query)
        result_text = str(response)
        logging.info(f"Coordinator 响应长度: {len(result_text)}")

        update_status("done", "分析完成")
    except Exception as e:
        logging.error(f"分析任务失败: {e}")
        update_status("failed", str(e))


async def _execute_analysis_with_feedback(
    task_id: str,
    file_paths: List[str],
    file_names: List[str],
    original_config: dict,
    feedback: FeedbackRequest,
):
    """基于反馈重跑的简化流水线（跳过 Fetcher）"""
    from app.agents.coordinator_agent import coordinator

    def update_status(status: str, progress: str):
        with LocalSession() as db:
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                task.status = status
                task.progress = progress
                if status in ("done", "failed"):
                    task.completed_at = datetime.now().isoformat(timespec="seconds")
                db.commit()

    try:
        update_status("analyzing", "正在基于反馈重新分析...")

        missing_str = ", ".join(feedback.missing_items) if feedback.missing_items else "无"
        query = (
            f"用户对之前的报告不满意，反馈如下:\n"
            f"满意度: {feedback.satisfaction}\n"
            f"缺失内容: {missing_str}\n"
            f"详细描述: {feedback.description or '无'}\n\n"
            f"原始分析配置: {json.dumps(original_config, ensure_ascii=False)}\n\n"
            f"请直接调用 analyzer_agent 追加缺失的分析方法，"
            f"然后调用 visualizer_agent 重新生成报告。不需要重新解析文件。\n"
            f"文件列表:\n" + "\n".join(f"- {n} ({p})" for n, p in zip(file_names, file_paths))
        )

        response = await coordinator.invoke_async(query)
        logging.info(f"反馈重跑响应: {len(str(response))} 字符")

        update_status("done", "基于反馈重新分析完成")
    except Exception as e:
        logging.error(f"反馈重跑失败: {e}")
        update_status("failed", str(e))
```

- [ ] **Step 2: 语法验证**

```bash
python -m py_compile app/api/api.py && echo "OK" || echo "FAIL"
```

- [ ] **Step 3: 提交**

```bash
git add app/api/api.py
git commit -m "feat: rewrite API - analysis run, feedback, templates endpoints"
```

---

## 阶段 7：模板系统

### Task 7.1: 创建 template_loader.py

**Files:**
- Create: `app/config/template_loader.py`

- [ ] **Step 1: 创建文件**

```python
"""
分析模板加载器

从 templates/ 目录加载 YAML 模板配置，提供查询接口。
"""
import os
from pathlib import Path
from typing import Optional, List, Dict
from yaml import safe_load

TEMPLATES_DIR = Path(__file__).parents[2] / "templates"
_cache: Dict[str, dict] = {}


def load_all_templates() -> Dict[str, dict]:
    """加载所有模板到内存"""
    global _cache
    _cache = {}
    if not TEMPLATES_DIR.exists():
        return _cache
    for f in TEMPLATES_DIR.glob("*.yml"):
        with open(f, "r", encoding="utf-8") as fh:
            data = safe_load(fh)
            if data and "id" in data:
                _cache[data["id"]] = data
    return _cache


def get_template(template_id: str) -> Optional[dict]:
    """获取单个模板"""
    if not _cache:
        load_all_templates()
    return _cache.get(template_id)


def list_templates() -> List[dict]:
    """列出所有模板（不含完整配置，只返回摘要）"""
    if not _cache:
        load_all_templates()
    return [
        {
            "id": t.get("id"),
            "name": t.get("name"),
            "description": t.get("description"),
            "icon": t.get("icon", "📊"),
            "file_types": t.get("applicable", {}).get("file_types", []),
            "keywords": t.get("applicable", {}).get("keywords", []),
        }
        for t in _cache.values()
    ]


# 启动时自动加载
load_all_templates()
```

- [ ] **Step 2: 语法验证 + 提交**

```bash
python -m py_compile app/config/template_loader.py && echo "OK" || echo "FAIL"
git add app/config/template_loader.py
git commit -m "feat: add template_loader.py - YAML template management"
```

---

### Task 7.2: 创建 6 个分析模板

**Files:**
- Create: `templates/statistical_summary.yml`
- Create: `templates/text_extraction.yml`
- Create: `templates/comparative_analysis.yml`
- Create: `templates/financial_audit.yml`
- Create: `templates/performance_review.yml`
- Create: `templates/comprehensive_report.yml`

- [ ] **Step 1: 创建 `templates/statistical_summary.yml`**

```yaml
id: statistical_summary
name: "数据统计分析"
description: "对表格数据进行统计摘要、趋势分析、异常检测和排名"
icon: "📊"
applicable:
  file_types: [xlsx, xls, csv]
  keywords: [统计, 分析, 趋势, 排名, 异常]
  min_files: 1
  max_files: 1
analysis:
  methods:
    - statistical_summary
    - trend_analysis
    - anomaly_detection
    - ranking
  hints:
    auto_detect_columns: true
report:
  template: executive_dashboard
  title_template: "{{file_name}} — 数据统计分析报告"
  sections:
    - summary_cards
    - trend_chart
    - anomaly_table
    - ranking_chart
    - recommendations
```

- [ ] **Step 2: 创建 `templates/text_extraction.yml`**

```yaml
id: text_extraction
name: "文档要点提取"
description: "对 Word 或 PDF 文档提取关键要点、分类整理和关键词统计"
icon: "📝"
applicable:
  file_types: [docx, pdf]
  keywords: [文档, 摘要, 要点, 提取, 分类]
  min_files: 1
  max_files: 1
analysis:
  methods:
    - text_summary
    - classification
  hints:
    auto_detect_columns: false
report:
  template: minimal_report
  title_template: "{{file_name}} — 文档要点提取报告"
  sections:
    - summary_cards
    - text_content
    - classification
```

- [ ] **Step 3: 创建 `templates/comparative_analysis.yml`**

```yaml
id: comparative_analysis
name: "对比分析"
description: "对两个及以上表格文件进行横向对比，找出差异和共同点"
icon: "📋"
applicable:
  file_types: [xlsx, xls, csv]
  keywords: [对比, 比较, 差异, 同比, 环比]
  min_files: 2
  max_files: 5
analysis:
  methods:
    - statistical_summary
    - comparison
    - trend_analysis
    - ranking
  hints:
    auto_detect_columns: true
report:
  template: executive_dashboard
  title_template: "多文件对比分析报告"
  sections:
    - summary_cards
    - comparison_chart
    - trend_chart
    - difference_table
    - recommendations
```

- [ ] **Step 4: 创建 `templates/financial_audit.yml`**

```yaml
id: financial_audit
name: "财务审计分析"
description: "分析财务报表，识别支出趋势、异常科目、结构占比和排名"
icon: "💰"
applicable:
  file_types: [xlsx, xls, csv]
  keywords: [财务, 支出, 预算, 科目, 审计, 经费, 资金]
  min_files: 1
  max_files: 1
analysis:
  methods:
    - statistical_summary
    - trend_analysis
    - anomaly_detection
    - ranking
    - composition
  hints:
    time_column: "日期"
    metric_columns: ["金额", "支出", "收入", "预算"]
    category_column: "科目"
report:
  template: executive_dashboard
  title_template: "{{file_name}} — 财务审计分析报告"
  sections:
    - summary_cards
    - trend_chart
    - composition_pie
    - anomaly_table
    - ranking_chart
    - recommendations
```

- [ ] **Step 5: 创建 `templates/performance_review.yml`**

```yaml
id: performance_review
name: "绩效评估分析"
description: "对比目标与实际数据，识别达标/未达标项，进行排名和趋势分析"
icon: "🎯"
applicable:
  file_types: [xlsx, xls, csv]
  keywords: [绩效, 考核, 指标, 达标, 目标, 完成率]
  min_files: 1
  max_files: 2
analysis:
  methods:
    - statistical_summary
    - comparison
    - ranking
    - anomaly_detection
    - trend_analysis
  hints:
    auto_detect_columns: true
report:
  template: executive_dashboard
  title_template: "{{file_name}} — 绩效评估分析报告"
  sections:
    - summary_cards
    - comparison_chart
    - ranking_chart
    - anomaly_table
    - recommendations
```

- [ ] **Step 6: 创建 `templates/comprehensive_report.yml`**

```yaml
id: comprehensive_report
name: "综合报告"
description: "完整分析：统计摘要 + 趋势 + 异常 + 排名 + 文本提取（全部分析方法）"
icon: "📑"
applicable:
  file_types: [xlsx, xls, csv, docx, pdf]
  keywords: [综合, 全面, 完整, 详细, 报告]
  min_files: 1
  max_files: 5
analysis:
  methods:
    - statistical_summary
    - trend_analysis
    - anomaly_detection
    - ranking
    - correlation
    - text_summary
    - comparison
    - classification
  hints:
    auto_detect_columns: true
report:
  template: executive_dashboard
  title_template: "{{file_name}} — 综合分析报告"
  sections:
    - summary_cards
    - trend_chart
    - composition_pie
    - anomaly_table
    - ranking_chart
    - text_content
    - recommendations
```

- [ ] **Step 7: 提交**

```bash
git add templates/
git commit -m "feat: add 6 analysis templates (stats, text, comparison, finance, performance, comprehensive)"
```

---

### Task 7.3: 创建报告 HTML 模板

**Files:**
- Create: `report_templates/executive_dashboard.html`
- Create: `report_templates/minimal_report.html`

- [ ] **Step 1: 创建 `report_templates/executive_dashboard.html`**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif; background: #f8fafc; color: #1e293b; line-height: 1.6; }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        .header { background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); color: #fff; padding: 48px 0 32px; margin-bottom: 32px; }
        .header h1 { font-size: 28px; margin-bottom: 8px; }
        .header p { opacity: 0.85; font-size: 14px; }
        .section-title { font-size: 20px; font-weight: 600; margin: 32px 0 16px; padding-bottom: 8px; border-bottom: 2px solid #e2e8f0; }
        .cards { display: flex; gap: 16px; flex-wrap: wrap; margin: 24px 0; }
        .chart-container { background: #fff; border-radius: 8px; padding: 24px; margin: 16px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
        .chart-container canvas { max-height: 350px; }
        table { width: 100%; border-collapse: collapse; margin: 16px 0; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
        th { background: #f1f5f9; padding: 12px; text-align: left; font-weight: 600; border-bottom: 2px solid #e2e8f0; }
        td { padding: 12px; border-bottom: 1px solid #f1f5f9; }
        .insight-box { background: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px 20px; margin: 16px 0; border-radius: 4px; }
        .footer { text-align: center; padding: 32px 0; color: #94a3b8; font-size: 12px; }
        {{ extra_styles }}
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>{{ title }}</h1>
            <p>{{ subtitle }}</p>
        </div>
    </div>

    <div class="container">
        {{ content }}
    </div>

    <div class="footer">
        <p>由多 Agent 数据分析平台自动生成 · {{ generated_at }}</p>
    </div>

    <script>
        document.addEventListener("DOMContentLoaded", function () {
            {{ chart_scripts }}
        });
    </script>
</body>
</html>
```

- [ ] **Step 2: 创建 `report_templates/minimal_report.html`**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif; background: #fff; color: #333; line-height: 1.8; max-width: 800px; margin: 0 auto; padding: 40px 20px; }
        h1 { font-size: 24px; margin-bottom: 8px; color: #1e40af; }
        h2 { font-size: 18px; margin: 32px 0 12px; padding-bottom: 4px; border-bottom: 1px solid #e5e7eb; }
        .meta { color: #6b7280; font-size: 14px; margin-bottom: 24px; }
        .content { font-size: 15px; }
        .footer { margin-top: 48px; padding-top: 16px; border-top: 1px solid #e5e7eb; color: #9ca3af; font-size: 12px; }
        {{ extra_styles }}
    </style>
</head>
<body>
    <h1>{{ title }}</h1>
    <p class="meta">{{ subtitle }}</p>
    <div class="content">
        {{ content }}
    </div>
    <div class="footer">
        <p>由多 Agent 数据分析平台自动生成 · {{ generated_at }}</p>
    </div>
</body>
</html>
```

- [ ] **Step 3: 提交**

```bash
git add report_templates/
git commit -m "feat: add 2 HTML report templates (dashboard + minimal)"
```

---

## 阶段 8：主入口更新

### Task 8.1: 更新 main.py

**Files:**
- Modify: `main.py`

- [ ] **Step 1: 重写 `main.py`**

```python
"""多 Agent 数据分析平台 — FastAPI 入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api import router as core_router
from app.api.upload import router as upload_router
from app.api.tasks import router as tasks_router
from app.api.reports import router as reports_router

app = FastAPI(
    title="Multi-Agent Data Analysis Platform",
    version="1.0.0",
    description="通用多 Agent 数据分析平台 — 上传文件，选择模板，获取报告",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(core_router)
app.include_router(upload_router)
app.include_router(tasks_router)
app.include_router(reports_router)


if __name__ == "__main__":
    import uvicorn
    from app.config.setting import settings
    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=True)
```

- [ ] **Step 2: 语法验证 + 提交**

```bash
python -m py_compile main.py && echo "OK" || echo "FAIL"
git add main.py
git commit -m "feat: update main.py - register all API routers"
```

---

### Task 8.2: 更新 run.py 和 requirements.txt

**Files:**
- Modify: `run.py`
- Modify: `requirements.txt`

- [ ] **Step 1: 更新 `run.py`**

```python
"""启动脚本"""
import uvicorn
from app.config.setting import settings

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
    )
```

- [ ] **Step 2: 更新 `requirements.txt`**

```
# Agent 框架
strands-agents

# Web 框架
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
python-multipart>=0.0.6

# 数据库
sqlalchemy>=2.0.0

# 配置
pydantic>=2.0.0
pydantic-settings>=2.0.0
pyyaml>=6.0
python-dotenv>=1.0.0

# 文件解析
openpyxl>=3.1.0
python-docx>=1.1.0
pypdf>=4.0.0

# HTML 模板
jinja2>=3.1.0

# 邮件（可选）
certifi>=2023.0.0
```

- [ ] **Step 3: 提交**

```bash
python -m py_compile run.py && echo "OK" || echo "FAIL"
git add run.py requirements.txt
git commit -m "feat: update run.py and requirements.txt for new platform"
```

---

## 阶段 9：示例数据

### Task 9.1: 创建示例数据文件

**Files:**
- Create: `examples/sample_sales.xlsx`
- Create: `examples/sample_report.docx`
- Create: `examples/README.md`

- [ ] **Step 1: 创建 `examples/README.md`**

```markdown
# 示例数据说明

本目录包含用于测试多 Agent 数据分析平台的示例文件。

## 使用步骤

1. 启动平台: `python run.py`
2. 上传示例文件到 POST /api/upload
3. 发起分析:
   - sample_sales.xlsx → 选择 "数据统计分析" 或 "财务审计分析" 模板
   - sample_report.docx → 选择 "文档要点提取" 模板
4. 查看报告: GET /api/reports/{task_id}

## 文件说明

- `sample_sales.xlsx`: 模拟的月度销售数据，包含日期、类别、金额等列
- `sample_report.docx`: 模拟的政府工作报告摘录，包含多段文字和嵌入表格
```

- [ ] **Step 2: 创建示例 Excel 文件（用 Python 生成）**

由于无法直接创建二进制 xlsx 文件，我们创建一个 CSV 示例文件作为替代，用户可自行转换为 xlsx：

```csv
日期,类别,金额,数量,区域
2025-01-01,办公用品,12500.00,45,东区
2025-01-02,IT设备,89000.00,12,西区
2025-01-03,办公用品,9800.00,38,南区
2025-01-04,耗材,4500.00,120,北区
2025-01-05,IT设备,76000.00,8,东区
2025-01-06,办公用品,11200.00,42,西区
2025-01-07,耗材,5100.00,135,南区
2025-01-08,IT设备,92000.00,15,北区
2025-01-09,办公用品,10800.00,40,东区
2025-01-10,耗材,4800.00,128,西区
```

- [ ] **Step 3: 创建示例 Word 文档（用 Python 生成的内容描述）**

创建 `examples/sample_report_content.json` 告知用户如何生成 docx：

```json
{
  "instruction": "将此 JSON 中的内容用 Word 保存为 sample_report.docx",
  "title": "2025年上半年工作总结",
  "paragraphs": [
    "2025年上半年，在区委区政府的正确领导下，我局紧紧围绕年度工作目标，扎实推进各项工作，取得了显著成效。",
    "一、主要工作完成情况。上半年共完成行政审批事项1256件，同比增长15.3%，按时办结率100%。",
    "二、重点项目推进。区重点项目共32个，已开工28个，开工率87.5%，完成投资额12.8亿元。",
    "三、民生保障工作。发放低保金2350万元，惠及困难群众1.2万户；完成老旧小区改造18个。",
    "四、存在问题。部分项目推进速度偏慢，资金拨付流程有待优化，基层服务能力仍需加强。",
    "五、下半年工作计划。加快推进剩余4个重点项目开工，优化资金审批流程，提升基层服务水平。"
  ]
}
```

- [ ] **Step 4: 用 Python 脚本生成示例 xlsx**

```bash
cd examples
python -c "
import openpyxl
wb = openpyxl.Workbook()
ws = wb.active
ws.title = '销售数据'
ws.append(['日期', '类别', '金额', '数量', '区域'])
data = [
    ('2025-01-01', '办公用品', 12500.00, 45, '东区'),
    ('2025-01-02', 'IT设备', 89000.00, 12, '西区'),
    ('2025-01-03', '办公用品', 9800.00, 38, '南区'),
    ('2025-01-04', '耗材', 4500.00, 120, '北区'),
    ('2025-01-05', 'IT设备', 76000.00, 8, '东区'),
    ('2025-02-01', '办公用品', 13100.00, 48, '西区'),
    ('2025-02-02', 'IT设备', 91000.00, 14, '南区'),
    ('2025-02-03', '耗材', 4700.00, 115, '北区'),
    ('2025-02-04', '办公用品', 10500.00, 41, '东区'),
    ('2025-02-05', 'IT设备', 85000.00, 10, '西区'),
    ('2025-03-01', '办公用品', 12800.00, 44, '南区'),
    ('2025-03-02', 'IT设备', 93000.00, 16, '北区'),
    ('2025-03-03', '耗材', 4900.00, 130, '东区'),
    ('2025-03-04', '办公用品', 11200.00, 43, '西区'),
    ('2025-03-05', 'IT设备', 88000.00, 11, '南区'),
    ('2025-04-01', '办公用品', 13500.00, 50, '北区'),
    ('2025-04-02', 'IT设备', 95000.00, 18, '东区'),
    ('2025-04-03', '耗材', 5200.00, 140, '西区'),
    ('2025-04-04', '办公用品', 10900.00, 39, '南区'),
    ('2025-04-05', 'IT设备', 82000.00, 9, '北区'),
    ('2025-05-01', '办公用品', 980000.00, 42, '东区'),
    ('2025-05-02', 'IT设备', 87000.00, 13, '西区'),
    ('2025-05-03', '耗材', 4600.00, 122, '南区'),
    ('2025-05-04', '办公用品', 11600.00, 46, '北区'),
    ('2025-05-05', 'IT设备', 90000.00, 15, '东区'),
    ('2025-06-01', '办公用品', 12100.00, 44, '西区'),
    ('2025-06-02', 'IT设备', 94000.00, 17, '南区'),
    ('2025-06-03', '耗材', 5000.00, 133, '北区'),
    ('2025-06-04', '办公用品', 10700.00, 40, '东区'),
    ('2025-06-05', 'IT设备', 86000.00, 12, '西区'),
]
for row in data:
    ws.append(row)
wb.save('sample_sales.xlsx')
print(f'Created sample_sales.xlsx with {len(data)} rows')
"
```

- [ ] **Step 5: 提交**

```bash
git add examples/
git commit -m "feat: add example data files and usage guide"
```

---

## 阶段 10：最终验证

### Task 10.1: 零 IoT 残留验证

- [ ] **Step 1: 执行残留检查**

```bash
cd C:\Users\YZW04\Desktop\开源技术\mutli-agents-main
echo "=== 检查 IoT 术语残留 ==="
grep -r "device_model\|app_rates\|firmware_rates\|app_speeds\|firmware_speeds" app/ --include="*.py" && echo "残留发现!" || echo "零残留"
grep -r "连接率\|帧延迟\|P2P\|p2p\|get_and_upload" app/ --include="*.py" && echo "残留发现!" || echo "零残留"
grep -r "TbLiveConnection\|list_connection_statistics\|list_live_connection" app/ --include="*.py" && echo "残留发现!" || echo "零残留"
```

Expected output:
```
零残留
零残留
零残留
```

- [ ] **Step 2: Python 语法全量检查**

```bash
find . -name "*.py" -not -path "./.claude/*" -not -path "./.idea/*" -exec python -m py_compile {} \; 2>&1 && echo "ALL OK" || echo "FAILURES FOUND"
```

- [ ] **Step 3: 检查目录完整性**

```bash
echo "=== 必须存在的关键文件 ==="
for f in \
  main.py run.py config.yml requirements.txt \
  app/agents/__init__.py app/agents/coordinator_agent.py \
  app/agents/fetcher_agent.py app/agents/analyzer_agent.py \
  app/agents/visualizer_agent.py \
  app/tools/__init__.py app/tools/file_tools.py \
  app/tools/analysis_tools.py app/tools/viz_tools.py \
  app/tools/storage_tools.py app/tools/email_tools.py \
  app/prompt/__init__.py app/prompt/coordinator_prompt.py \
  app/prompt/fetcher_prompt.py app/prompt/analyzer_prompt.py \
  app/prompt/visualizer_prompt.py \
  app/models/LLM_model.py app/models/database.py \
  app/api/api.py app/api/upload.py app/api/tasks.py app/api/reports.py \
  app/config/setting.py app/config/template_loader.py \
  templates/statistical_summary.yml templates/text_extraction.yml \
  templates/comparative_analysis.yml templates/financial_audit.yml \
  templates/performance_review.yml templates/comprehensive_report.yml \
  report_templates/executive_dashboard.html report_templates/minimal_report.html
do
  if [ -f "$f" ]; then echo "✅ $f"; else echo "❌ MISSING: $f"; fi
done

echo ""
echo "=== 不应存在的 IoT 残留文件 ==="
for f in \
  app/agents/lead_agent.py app/agents/data_query_agent.py \
  app/agents/data_analyst_agent.py app/agents/web_engineer_agent.py \
  app/agents/html_report_review_agent.py app/agents/summary_html_agent.py \
  app/agents/zip_file_agent.py app/agents/send_email_agent.py \
  app/db/ app/servics/ \
  app/config/setting_env.py app/config/setting_sql.py \
  app/tools/strands_agents_tool.py
do
  if [ -e "$f" ]; then echo "❌ 残留: $f"; else echo "✅ 已清除: $f"; fi
done
```

- [ ] **Step 4: 提交最终状态**

```bash
git add -A
git commit -m "chore: final verification - zero IoT residue, all 39+ files validated"
```

---

## 实施完成标准

全部 10 个阶段完成后，系统应满足：

1. ✅ 可上传 Excel/CSV/Word/PDF 文件
2. ✅ 可选择 6 个分析模板或输入自然语言描述
3. ✅ 4 个 Agent 协作完成 文件解析 → 数据分析 → HTML 报告
4. ✅ 报告包含 Chart.js 交互式图表
5. ✅ 支持用户反馈 → 自动重跑追加分析
6. ✅ 零 IoT 术语残留
7. ✅ 所有 Python 文件通过语法检查
8. ✅ 关键文件完整性检查通过
