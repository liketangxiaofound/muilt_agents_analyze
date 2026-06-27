"""知识库问答端点 — 集成三层记忆"""
import uuid
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from strands import Agent

from app.models.LLM_model import ModelInstances
from app.models.knowledge_base import list_collection_names, get_collection_info
from app.models.memory_manager import memory
from app.prompt.knowledge_prompt import knowledge_prompt
from app.tools.knowledge_tools import search_knowledge, list_collections, get_document_content

router = APIRouter()


class KnowledgeAskRequest(BaseModel):
    question: str
    collection: Optional[str] = None
    session_id: Optional[str] = None  # 不传则自动创建新会话


@router.get("/api/knowledge/collections")
async def get_collections():
    """获取所有可用知识库"""
    collections = []
    for name in list_collection_names():
        info = get_collection_info(name)
        collections.append(info)
    return {"collections": collections}


@router.post("/api/knowledge/ask")
async def ask_knowledge(request: KnowledgeAskRequest):
    """向知识库提问（带三层记忆注入）"""
    if not request.question.strip():
        raise HTTPException(400, "问题不能为空")

    session_id = request.session_id or uuid.uuid4().hex[:8]

    # ── 加载三层记忆 ──
    long_term = memory.load_long_term()
    daily_relevant = memory.search_relevant_daily(request.question, days=7, top_k=3)
    session_content = memory.get_recent_rounds(session_id, n=5)

    # ── 组装 System Prompt（注入记忆） ──
    memory_section = _build_memory_section(long_term, daily_relevant, session_content)
    full_prompt = knowledge_prompt + memory_section

    # ── 创建带记忆的 Agent 实例 ──
    agent = Agent(
        system_prompt=full_prompt,
        model=ModelInstances.LEADER_MODEL,
        tools=[search_knowledge, list_collections, get_document_content],
    )

    # ── 构造 query ──
    if request.collection:
        query = (
            f"请在知识库 '{request.collection}' 中检索以下问题的答案。"
            f"先用 search_knowledge 检索相关内容，然后整合答案: {request.question}"
        )
    else:
        query = (
            f"请检索所有知识库，查找以下问题的答案。"
            f"先用 list_collections 查看可用知识库，然后用 search_knowledge 检索: {request.question}"
        )

    try:
        response = await agent.invoke_async(query)
        answer = str(response)

        # ── 写回会话记忆 ──
        memory.append_session(session_id, request.question, answer)

        # ── 超 5 轮自动压缩旧轮次到日记忆 ──
        memory.maybe_compress(session_id, max_rounds=5)

        return {
            "session_id": session_id,
            "question": request.question,
            "collection": request.collection,
            "answer": answer,
        }
    except Exception as e:
        logging.error(f"知识库问答出错: {e}")
        raise HTTPException(500, f"知识库问答出错: {str(e)}")


@router.get("/api/knowledge/session/{session_id}")
async def get_session_memory(session_id: str):
    """查看当前会话记忆"""
    content = memory.load_session(session_id)
    rounds = memory.count_rounds(session_id)
    return {
        "session_id": session_id,
        "rounds": rounds,
        "content_preview": content[-2000:] if len(content) > 2000 else content,
    }


@router.post("/api/knowledge/session/{session_id}/close")
async def close_session(session_id: str):
    """手动关闭会话——压缩全部内容到日记忆并清空会话文件"""
    old_rounds = memory.count_rounds(session_id)
    if old_rounds > 0:
        content = memory.load_session(session_id)
        summary = memory._llm_compress(content)
        memory.append_daily(f"### 会话 {session_id}（已关闭）\n{summary}")

    # 清空会话文件
    path = memory._session_path(session_id)
    if __import__("os").path.exists(path):
        __import__("os").remove(path)

    return {"session_id": session_id, "status": "closed", "compressed_rounds": old_rounds}


# ================================================================
# 辅助函数
# ================================================================

def _build_memory_section(long_term: str, daily: str, session: str) -> str:
    """将三层记忆拼装为 prompt 段落"""
    parts = []
    if session:
        parts.append(f"## 当前会话历史\n\n{session}")
    if daily:
        parts.append(f"## 近期相关对话（按日期）\n\n{daily}")
    if long_term:
        parts.append(f"## 长期记忆（管理员维护的核心事实与偏好）\n\n{long_term}")
    if not parts:
        return ""
    return "\n\n---\n\n" + "\n\n---\n\n".join(parts)
