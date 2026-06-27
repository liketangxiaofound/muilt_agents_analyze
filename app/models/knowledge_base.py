"""
ChromaDB 知识库管理 — 纯 TF-IDF 嵌入，零模型下载。

Embedding: sklearn TfidfVectorizer, 字符级 1-2 gram, 384维。
"""
import os
import logging
from typing import List, Dict, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.api.types import Documents, Embeddings

from app.config.setting import settings

# ChromaDB 持久化目录
CHROMA_PATH = os.path.join(settings.storage_dir, "chromadb")
os.makedirs(CHROMA_PATH, exist_ok=True)

# 知识文档存放目录
KNOWLEDGE_DOCS_PATH = os.path.join(settings.storage_dir, "knowledge_docs")
os.makedirs(KNOWLEDGE_DOCS_PATH, exist_ok=True)


# ============================================================
# 自定义 TF-IDF Embedding Function（纯本地，零下载）
# ============================================================

class TfidfEmbeddingFunction:
    """基于 sklearn TfidfVectorizer 的中文友好 embedding。

    - 零模型下载，纯离线可用
    - 字符级 n-gram (1-2) 适配中文
    - 固定维度 384，兼容 ChromaDB
    - 首次 add 时自动 fit 词汇表
    """

    def __init__(self):
        self._vectorizer = None
        self._dim = 384

    def name(self) -> str:
        return "tfidf-char-ngram-384"

    def _ensure_fitted(self, texts: List[str]):
        from sklearn.feature_extraction.text import TfidfVectorizer

        self._vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(1, 2),
            max_features=self._dim,
            lowercase=False,
        )
        self._vectorizer.fit(texts)
        logging.info(f"TF-IDF 词汇表已构建: {len(self._vectorizer.vocabulary_)} 个特征")

    def __call__(self, input: Documents) -> Embeddings:
        import numpy as np
        texts = list(input)

        if self._vectorizer is None:
            self._ensure_fitted(texts)

        vectors = self._vectorizer.transform(texts).toarray()

        n_samples = vectors.shape[0]
        padded = np.zeros((n_samples, self._dim), dtype=np.float32)
        actual_dim = min(vectors.shape[1], self._dim)
        padded[:, :actual_dim] = vectors[:, :actual_dim]

        norms = np.linalg.norm(padded, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        padded = padded / norms

        return padded.tolist()

    def embed_query(self, input):
        """ChromaDB >=1.5 查询嵌入 — 兼容 str 和 list"""
        if isinstance(input, str):
            return self([input])[0]
        return self(input)  # list case

    def embed_documents(self, input):
        """ChromaDB >=1.5 文档嵌入"""
        return self(input)


# ---- 全局 embedding 函数 ----
_embedding_fn = TfidfEmbeddingFunction()

# ---- 初始化 ChromaDB 客户端 ----
os.environ.setdefault("NO_PROXY", "localhost,127.0.0.1,.local")
_client = chromadb.PersistentClient(
    path=CHROMA_PATH,
    settings=ChromaSettings(anonymized_telemetry=False),
)


def _get_collection(name: str):
    """获取 collection，始终显式传入 TF-IDF embedding，防止 ChromaDB 回退到 ONNX。"""
    return _client.get_collection(name, embedding_function=_embedding_fn)


def get_or_create_collection(name: str):
    """获取或创建 Collection"""
    return _client.get_or_create_collection(
        name=name,
        metadata={"description": f"知识库: {name}"},
        embedding_function=_embedding_fn,
    )


def list_collection_names() -> List[str]:
    """列出所有可用的知识库"""
    return [c.name for c in _client.list_collections()]


def get_collection_info(name: str) -> Dict:
    """获取知识库信息"""
    try:
        col = _get_collection(name)
        count = col.count()
        return {"name": name, "document_count": count, "metadata": col.metadata}
    except Exception:
        return {"name": name, "document_count": 0, "error": "知识库不存在"}


def rerank_by_keyword_overlap(query: str, results: List[Dict]) -> List[Dict]:
    """基于关键词重叠度对检索结果二次排序。"""
    if not results or len(results) <= 1:
        return results

    import re
    keywords = []
    eng_words = re.findall(r'[a-zA-Z]{2,}', query)
    keywords.extend(w.lower() for w in eng_words)
    chinese_chars = re.findall(r'[一-鿿]', query)
    for i in range(len(chinese_chars) - 1):
        keywords.append(chinese_chars[i] + chinese_chars[i + 1])

    if not keywords:
        return results

    for r in results:
        if not isinstance(r, dict) or "content" not in r:
            continue
        content_lower = r["content"].lower()
        hits = sum(1 for kw in keywords if kw in content_lower)
        overlap_score = hits / len(keywords)
        original_score = r.get("score", 0.5)
        r["score"] = round(original_score * 0.7 + overlap_score * 0.3, 4)
        r["_keyword_hits"] = hits

    results.sort(key=lambda x: x.get("score", 0) if isinstance(x, dict) else 0, reverse=True)
    return results


def search_collection(collection_name: str, query: str, n_results: int = 5) -> List[Dict]:
    """在指定知识库中检索，结果经关键词重排序"""
    try:
        col = _get_collection(collection_name)
        fetch_n = min(n_results * 2, 20)
        results = col.query(query_texts=[query], n_results=fetch_n)
        formatted = _format_results(results)
        formatted = rerank_by_keyword_overlap(query, formatted)
        return formatted[:n_results]
    except Exception as e:
        logging.error(f"知识库检索失败 [{collection_name}]: {e}")
        return [{"error": f"检索失败: {str(e)}"}]


def search_all(query: str, n_results: int = 3) -> Dict[str, List[Dict]]:
    """在所有知识库中检索"""
    all_results = {}
    for name in list_collection_names():
        results = search_collection(name, query, n_results)
        all_results[name] = results
    return all_results


def add_documents(
    collection_name: str,
    documents: List[str],
    metadatas: Optional[List[Dict]] = None,
    ids: Optional[List[str]] = None,
) -> Dict:
    """向知识库添加文档"""
    col = get_or_create_collection(collection_name)
    if ids is None:
        import uuid
        ids = [uuid.uuid4().hex[:8] for _ in documents]
    if metadatas is None:
        metadatas = [{"source": "manual"} for _ in documents]

    col.add(documents=documents, metadatas=metadatas, ids=ids)
    return {"collection": collection_name, "added": len(documents), "ids": ids}


def index_document_file(
    collection_name: str,
    file_path: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100,
) -> Dict:
    """将知识文档文件分块后索引入库。支持 .txt/.md。"""
    if not os.path.exists(file_path):
        return {"error": f"文档不存在: {file_path}"}

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    chunks = []
    current_chunk = ""
    for p in paragraphs:
        if len(current_chunk) + len(p) < chunk_size:
            current_chunk += p + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            if len(p) > chunk_size:
                sentences = _split_by_sentence(p)
                sub_chunk = ""
                for s in sentences:
                    if len(sub_chunk) + len(s) < chunk_size:
                        sub_chunk += s
                    else:
                        if sub_chunk:
                            chunks.append(sub_chunk.strip())
                        sub_chunk = s
                if sub_chunk:
                    current_chunk = sub_chunk + "\n\n"
                else:
                    current_chunk = ""
            else:
                current_chunk = p + "\n\n"
    if current_chunk:
        chunks.append(current_chunk.strip())
    if not chunks:
        chunks = [content[:chunk_size]]

    if chunk_overlap > 0 and len(chunks) > 1:
        overlapped_chunks = []
        for i, chunk in enumerate(chunks):
            if i > 0:
                prev_tail = chunks[i - 1][-chunk_overlap:] if len(chunks[i - 1]) > chunk_overlap else chunks[i - 1]
                chunk = prev_tail + "\n\n" + chunk
            overlapped_chunks.append(chunk)
        chunks = overlapped_chunks

    filename = os.path.basename(file_path)
    metadatas = [
        {"source": filename, "chunk_index": i, "total_chunks": len(chunks),
         "file_path": file_path, "has_prev": i > 0, "has_next": i < len(chunks) - 1}
        for i in range(len(chunks))
    ]
    return add_documents(collection_name, chunks, metadatas)


def _split_by_sentence(text: str) -> list:
    import re
    sentences = re.split(r'(?<=[。！？；.!?;])\s*', text)
    return [s for s in sentences if s.strip()]


def _format_results(results: Dict) -> List[Dict]:
    formatted = []
    if not results or "ids" not in results or not results["ids"]:
        return formatted
    ids_list = results["ids"][0] if results["ids"] else []
    docs_list = results["documents"][0] if results["documents"] else []
    metas_list = results["metadatas"][0] if results["metadatas"] else []
    distances = results.get("distances", [[]])[0] if results.get("distances") else []
    for i in range(len(ids_list)):
        item = {
            "id": ids_list[i] if i < len(ids_list) else "",
            "content": docs_list[i][:800] if i < len(docs_list) else "",
            "source": metas_list[i].get("source", "未知") if i < len(metas_list) else "未知",
        }
        if i < len(distances):
            item["score"] = round(1 - distances[i], 4)
        formatted.append(item)
    return formatted
