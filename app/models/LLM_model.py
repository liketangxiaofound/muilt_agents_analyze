"""
LLM 模型实例管理

配置方式（按优先级从高到低）：
1. 环境变量 — 通过 .env 文件或系统环境变量设置
   - DEEPSEEK_API_KEY    DeepSeek API 密钥
   - DEEPSEEK_BASE_URL   DeepSeek API 端点（默认 https://api.deepseek.com/v1）
   - DEEPSEEK_MODEL_ID   DeepSeek 模型 ID（默认 deepseek-chat）
   - LLM_MAX_TOKENS      最大输出 token 数（默认 8192）
   - LLM_TEMPERATURE     生成温度（默认 0.8）
   - LLM_TOP_P           Top-P 采样（默认 0.9）

2. 直接修改本文件中 ModelInstances.LEADER_MODEL 的初始化参数

示例 .env 文件内容：
   DEEPSEEK_API_KEY=sk-your-api-key-here
   DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
   DEEPSEEK_MODEL_ID=deepseek-chat
"""
import os
import logging
from dotenv import load_dotenv
from strands.models.openai import OpenAIModel

load_dotenv()


class ModelInstances:
    try:
        LEADER_MODEL = OpenAIModel(
            client_args={
                "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
                "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
            },
            model_id=os.getenv("DEEPSEEK_MODEL_ID", "deepseek-chat"),
            params={
                "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "8192")),
                "temperature": float(os.getenv("LLM_TEMPERATURE", "0.8")),
                "top_p": float(os.getenv("LLM_TOP_P", "0.9")),
            },
        )
    except Exception as e:
        logging.error(f"Failed to initialize LEADER_MODEL: {str(e)}")
        raise
