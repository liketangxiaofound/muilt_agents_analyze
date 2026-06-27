"""
知识库工具

提供 Agent 使用的知识库检索和查询能力。
"""
import json
import logging
from strands import tool
from app.models.knowledge_base import (
    search_collection,
    search_all,
    list_collection_names,
    get_collection_info,
)

# 每条检索结果最大字符数（超出截断，防止上下文膨胀）
MAX_RESULT_CHARS = 800


def _trim_results(results: list, max_chars: int = MAX_RESULT_CHARS) -> list:
    """截断每条检索结果的 content 字段"""
    trimmed = []
    for r in results:
        if isinstance(r, dict) and "content" in r and len(r["content"]) > max_chars:
            r = dict(r)
            r["content"] = r["content"][:max_chars] + "..."
            r["_truncated"] = True
        trimmed.append(r)
    return trimmed


def _trim_all_results(all_results: dict, max_chars: int = MAX_RESULT_CHARS) -> dict:
    """截断所有知识库的检索结果"""
    trimmed = {}
    for name, results in all_results.items():
        trimmed[name] = _trim_results(results, max_chars)
    return trimmed


@tool
def search_knowledge(query: str, collection: str = "", n_results: int = 5, max_chars: int = 800) -> str:
    """
    在知识库中语义检索相关内容。

    每条结果最多返回 max_chars 字符（默认800，最大2000）。需要完整内容时使用 get_document_content。

    参数:
        query:      检索问题或关键词
        collection: 知识库名称（policies/finance/manual/custom），留空则检索所有知识库
        n_results:  返回结果数量（最多 8 条）
        max_chars:  每条结果最大字符数（默认800）
    返回:
        JSON 格式的检索结果
    """
    n_results = min(n_results, 8)  # 硬上限
    max_chars = min(max_chars, 2000)  # 硬上限

    if collection and collection.strip():
        results = search_collection(collection.strip(), query, n_results)
        results = _trim_results(results, max_chars)
        total_chars = sum(len(r.get("content", "")) for r in results if isinstance(r, dict))
        logging.info(f"检索 [{collection}]: {len(results)} 条结果, {total_chars} 字符")
        return json.dumps({
            "collection": collection.strip(),
            "query": query,
            "count": len(results),
            "results": results,
        }, ensure_ascii=False)
    else:
        all_results = search_all(query, n_results)
        all_results = _trim_all_results(all_results, max_chars)
        total_count = sum(len(v) for v in all_results.values())
        total_chars = sum(
            len(r.get("content", ""))
            for results in all_results.values()
            for r in results if isinstance(r, dict)
        )
        logging.info(f"检索全部知识库: {total_count} 条结果, {total_chars} 字符")
        return json.dumps({
            "query": query,
            "searched_collections": list(all_results.keys()),
            "total_results": total_count,
            "results_by_collection": all_results,
        }, ensure_ascii=False)


@tool
def list_collections() -> str:
    """
    列出所有可用的知识库及其基本信息。

    返回:
        JSON 格式的知识库列表
    """
    collections = []
    for name in list_collection_names():
        info = get_collection_info(name)
        collections.append(info)
    return json.dumps({"collections": collections}, ensure_ascii=False)


@tool
def get_document_content(document_id: str, collection: str) -> str:
    """
    获取指定文档的完整内容（通过 ID 精确查找）。

    参数:
        document_id: 文档 ID（来自 search_knowledge 返回的 id 字段）
        collection:  知识库名称
    返回:
        文档完整内容
    """
    import chromadb
    from app.models.knowledge_base import _client

    try:
        col = _client.get_collection(collection)
        result = col.get(ids=[document_id])
        if result and result["documents"]:
            return json.dumps({
                "id": document_id,
                "content": result["documents"][0],
                "metadata": result["metadatas"][0] if result["metadatas"] else {},
            }, ensure_ascii=False)
        return json.dumps({"error": "文档未找到"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"获取文档失败: {str(e)}"}, ensure_ascii=False)
