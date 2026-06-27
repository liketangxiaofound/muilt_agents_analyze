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
    Column, String, Integer, Text, ForeignKey,
    create_engine, event,
)
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config.setting import settings

# ---- 数据库引擎 ----
os.makedirs(settings.storage_dir, exist_ok=True)
DB_PATH = os.path.join(settings.storage_dir, "metadata.db")

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
    file_type   = Column(String, nullable=False)
    file_size   = Column(Integer)
    file_path   = Column(String, nullable=False)
    session_id  = Column(String, nullable=False)
    preview     = Column(Text)
    created_at  = Column(String, nullable=False, default=now_iso)


class Task(Base):
    __tablename__ = "tasks"

    id              = Column(String, primary_key=True, default=gen_id)
    upload_ids      = Column(Text, nullable=False)
    template_id     = Column(String)
    nl_query        = Column(Text)
    status          = Column(String, nullable=False, default="pending")
    progress        = Column(String)
    analysis_config = Column(Text)
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
print(f"SQLite 数据库已就绪: {DB_PATH}")
