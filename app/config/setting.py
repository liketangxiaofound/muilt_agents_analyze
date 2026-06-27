"""
应用配置管理

优先级: 命令行参数 > 环境变量 > config.yml 默认值
"""
import os
import sys
from pathlib import Path
from typing import List

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


def _load_settings() -> Setting:
    """加载 YAML 配置，环境变量可覆盖"""
    profile = sys.argv[1] if len(sys.argv) > 1 else None
    project_dir = Path(__file__).parents[2]

    config_file = f"config_{profile}.yml" if profile else "config.yml"
    config_path = project_dir / config_file

    if not config_path.exists():
        print(f"配置文件 {config_path} 不存在，使用默认配置")
        return Setting()

    with open(config_path, "r", encoding="utf-8") as f:
        data = safe_load(f) or {}

    # 环境变量覆盖 YAML
    data["port"] = int(os.getenv("APP_PORT", data.get("port", 8000)))
    data["storage_dir"] = os.getenv("APP_STORAGE_DIR", data.get("storage_dir", "./local_storage"))

    return Setting(**data)


settings = _load_settings()
print(f"配置加载完成: port={settings.port}, storage={settings.storage_dir}")
