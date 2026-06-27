"""
记忆管理模块 — 三层记忆架构

层级:
  长期记忆  → MEMORY.md                手动维护的核心事实/偏好/纠错
  日记忆    → daily/{YYYY}/{MM}/{DD}.md LLM 自动压缩的每日对话摘要
  会话记忆  → sessions/{session_id}.md  当前活跃会话的原始 Q&A

数据流:
  读取: 三层记忆 → 注入 System Prompt → Agent 执行
  写入: Agent 返回 → 追加会话记忆 → 超 5 轮触发压缩 → 写入日记忆
"""
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from app.config.setting import settings

MEMORY_ROOT = os.path.join(settings.storage_dir, "memory")


class MemoryManager:
    """三层记忆管理器"""

    def __init__(self):
        self._ensure_dirs()

    def _ensure_dirs(self):
        for sub in ["daily", "sessions"]:
            os.makedirs(os.path.join(MEMORY_ROOT, sub), exist_ok=True)
        # 确保 MEMORY.md 存在
        mem_path = os.path.join(MEMORY_ROOT, "MEMORY.md")
        if not os.path.exists(mem_path):
            with open(mem_path, "w", encoding="utf-8") as f:
                f.write("# 长期记忆\n\n> 此文件由管理员手动维护。\n")

    # ================================================================
    # 长期记忆 (MEMORY.md)
    # ================================================================

    def load_long_term(self) -> str:
        """读取长期记忆全文"""
        path = os.path.join(MEMORY_ROOT, "MEMORY.md")
        if not os.path.exists(path):
            return ""
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return content.strip()

    def add_long_term(self, entry: str):
        """追加一条长期记忆（管理员调用）"""
        path = os.path.join(MEMORY_ROOT, "MEMORY.md")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"\n- [{timestamp}] {entry}\n")

    # ================================================================
    # 日记忆 (daily/{YYYY}/{MM}/{DD}.md)
    # ================================================================

    def _daily_path(self, dt: datetime = None) -> str:
        """日记忆文件路径"""
        dt = dt or datetime.now()
        return os.path.join(MEMORY_ROOT, "daily", dt.strftime("%Y/%m/%d.md"))

    def load_daily(self, date_str: str = None) -> str:
        """读取指定日期的日记忆。date_str 格式: YYYY-MM-DD，默认今天"""
        if date_str:
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                return ""
        else:
            dt = datetime.now()
        path = self._daily_path(dt)
        if not os.path.exists(path):
            return ""
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def load_recent_daily(self, days: int = 7) -> list[dict]:
        """加载最近 N 天的日记忆，返回 [{"date": "...", "content": "..."}, ...]"""
        result = []
        for i in range(days):
            dt = datetime.now() - timedelta(days=i)
            path = self._daily_path(dt)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                if content:
                    result.append({
                        "date": dt.strftime("%Y-%m-%d"),
                        "content": content,
                    })
        return result

    def append_daily(self, content: str):
        """追加内容到今天日记忆"""
        path = self._daily_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"\n{content}\n")

    # ================================================================
    # 会话记忆 (sessions/{session_id}.md)
    # ================================================================

    def _session_path(self, session_id: str) -> str:
        return os.path.join(MEMORY_ROOT, "sessions", f"{session_id}.md")

    def load_session(self, session_id: str) -> str:
        """读取当前会话全文"""
        path = self._session_path(session_id)
        if not os.path.exists(path):
            return ""
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def append_session(self, session_id: str, question: str, answer: str):
        """追加一轮 Q&A 到会话文件"""
        path = self._session_path(session_id)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"\n## Q: {question}\n\n{answer}\n")

    def count_rounds(self, session_id: str) -> int:
        """统计当前会话的 Q&A 轮数"""
        content = self.load_session(session_id)
        if not content:
            return 0
        return content.count("## Q:")

    def get_recent_rounds(self, session_id: str, n: int = 5) -> str:
        """只返回最近 N 轮 Q&A"""
        content = self.load_session(session_id)
        if not content:
            return ""
        # 按 "## Q:" 分割，取最后 N 个
        parts = content.split("## Q:")
        # parts[0] 是第一个 Q: 之前的内容（通常为空）
        recent = parts[-n:] if len(parts) > n else parts[1:] if len(parts) > 1 else []
        if not recent:
            return content
        return "## Q:" + "## Q:".join(recent)

    # ================================================================
    # 压缩逻辑
    # ================================================================

    def maybe_compress(self, session_id: str, max_rounds: int = 5):
        """如果会话超过 max_rounds 轮，压缩旧轮次到日记忆"""
        total = self.count_rounds(session_id)
        if total <= max_rounds:
            return  # 不需要压缩

        content = self.load_session(session_id)
        parts = content.split("## Q:")
        # parts[1:] 是各轮 Q&A
        old_parts = parts[1:total - max_rounds + 1]  # 需要压缩的旧轮次
        recent_parts = parts[total - max_rounds + 1:]  # 保留的最近轮次

        if not old_parts:
            return

        old_text = "## Q:" + "## Q:".join(old_parts)
        summary = self._llm_compress(old_text)

        # 写入日记忆
        self.append_daily(f"### 会话 {session_id}\n{summary}")

        # 重写会话文件，只保留最近轮次
        path = self._session_path(session_id)
        with open(path, "w", encoding="utf-8") as f:
            f.write("## Q:" + "## Q:".join(recent_parts))

    def _llm_compress(self, text: str) -> str:
        """调 LLM 压缩对话为 3-5 条关键事实"""
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=os.getenv("DEEPSEEK_API_KEY", ""),
                base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
            )
            prompt = (
                "将以下用户与助手的对话压缩为 3-5 条关键事实。"
                "每条一行，使用 '- [类型]: 内容' 格式。"
                "类型包括: 用户偏好、知识纠正、高频问题、特殊需求。"
                "只保留对后续问答有价值的信息，丢弃寒暄和重复内容。\n\n"
            )
            response = client.chat.completions.create(
                model=os.getenv("DEEPSEEK_MODEL_ID", "deepseek-chat"),
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text[-6000:]},
                ],
                temperature=0.3,
                max_tokens=800,
            )
            return response.choices[0].message.content or "(压缩失败)"
        except Exception as e:
            import logging
            logging.warning(f"记忆压缩失败: {e}")
            # 降级: 简单截断
            lines = text.split("\n")
            summary_lines = [l for l in lines if l.strip() and not l.startswith("#")]
            return "\n".join(summary_lines[:10]) if summary_lines else "(截断)"

    # ================================================================
    # 语义筛选 — 从最近日记忆中选最相关的
    # ================================================================

    def search_relevant_daily(self, query: str, days: int = 7, top_k: int = 3) -> str:
        """
        用 ChromaDB 对最近 N 天的日记忆做语义检索，
        只返回与当前问题最相关的 K 条。
        """
        recent = self.load_recent_daily(days)
        if not recent:
            return ""

        # 如果日记忆总量不大，全量返回
        total_chars = sum(len(r["content"]) for r in recent)
        if total_chars < 3000:
            return "\n\n".join(
                f"### {r['date']}\n{r['content'][:1500]}" for r in recent
            )

        # 用 ChromaDB 做语义筛选
        try:
            from app.models.knowledge_base import _client as chroma_client

            collection_name = "daily_memory_search"
            try:
                col = chroma_client.get_collection(collection_name)
            except Exception:
                # 不存在则不筛选，回退全量
                return "\n\n".join(
                    f"### {r['date']}\n{r['content'][:800]}" for r in recent[-5:]
                )

            results = col.query(query_texts=[query], n_results=top_k)
            if not results or not results.get("ids") or not results["ids"][0]:
                return "\n\n".join(
                    f"### {r['date']}\n{r['content'][:800]}" for r in recent[-3:]
                )

            relevant_dates = set()
            docs = results.get("documents", [[]])[0]
            for doc in docs:
                for r in recent:
                    if r["content"][:100] in doc or doc[:100] in r["content"]:
                        relevant_dates.add(r["date"])

            filtered = [r for r in recent if r["date"] in relevant_dates]
            if not filtered:
                filtered = recent[-3:]

            return "\n\n".join(
                f"### {r['date']}\n{r['content'][:1000]}" for r in filtered
            )

        except Exception as e:
            import logging
            logging.warning(f"语义筛选日记忆失败: {e}")
            return "\n\n".join(
                f"### {r['date']}\n{r['content'][:800]}" for r in recent[-3:]
            )

    # ================================================================
    # 日记忆索引（每次追加日记忆后调用，保持 ChromaDB 同步）
    # ================================================================

    def index_daily_to_chromadb(self):
        """将日记忆索引入 ChromaDB 供语义检索"""
        try:
            from app.models.knowledge_base import _client as chroma_client

            collection_name = "daily_memory_search"
            try:
                col = chroma_client.get_collection(collection_name)
            except Exception:
                col = chroma_client.create_collection(
                    name=collection_name,
                    metadata={"description": "日记忆语义检索索引"},
                )

            recent = self.load_recent_daily(30)  # 最近 30 天
            ids_to_add, docs_to_add = [], []
            for r in recent:
                chunks = r["content"].split("\n### ")
                for ci, chunk in enumerate(chunks):
                    if len(chunk.strip()) > 50:
                        ids_to_add.append(f"{r['date']}-{ci}")
                        docs_to_add.append(chunk.strip())

            if ids_to_add:
                # 清空旧索引，重新构建（日记忆文件可能已变化）
                existing = col.get()
                if existing and existing.get("ids"):
                    col.delete(ids=existing["ids"])
                col.add(documents=docs_to_add, ids=ids_to_add)

        except Exception as e:
            import logging
            logging.warning(f"日记忆 ChromaDB 索引失败: {e}")


# ================================================================
# 全局单例
# ================================================================

memory = MemoryManager()
