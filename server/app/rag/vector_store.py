"""Chroma 向量库：切分、写入、检索与重建。"""
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.agents.llm import get_embeddings
from app.core.config import settings
from app.models.entities import Knowledge

_store = None


def get_store():
    """获取或创建持久化向量库，嵌入维度为 2048。"""
    global _store
    if _store is None:
        from langchain_chroma import Chroma

        _store = Chroma(
            collection_name=settings.CHROMA_COLLECTION,
            embedding_function=get_embeddings(),
            persist_directory=settings.CHROMA_DIR,
            collection_metadata={"hnsw:space": "cosine"},
        )
    return _store


def reset_store():
    """删除并清空当前知识库集合。"""
    global _store
    _store = None
    client = chromadb.PersistentClient(path=settings.CHROMA_DIR)
    try:
        client.delete_collection(settings.CHROMA_COLLECTION)
    except Exception:
        pass


def _split(content: str, title: str):
    """按中文标点切分知识正文。"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=80,
        separators=["\n\n", "\n", "。", "；", "，", " ", ""],
    )
    chunks = splitter.split_text(content or "")
    return chunks or [content or title]


def upsert_knowledge(knowledge_id: int, title: str, category: str, content: str) -> int:
    """按知识编号覆盖写入向量，返回切片数。"""
    store = get_store()
    try:
        store._collection.delete(where={"knowledge_id": int(knowledge_id)})
    except Exception:
        pass
    chunks = _split(content, title)
    metadatas = [
        {"knowledge_id": int(knowledge_id), "title": title, "category": category, "chunk": index}
        for index in range(len(chunks))
    ]
    ids = [f"k{knowledge_id}_{index}" for index in range(len(chunks))]
    store.add_texts(chunks, metadatas=metadatas, ids=ids)
    return len(chunks)


def delete_knowledge_vectors(knowledge_id: int):
    """删除某条知识对应的向量。"""
    try:
        get_store()._collection.delete(where={"knowledge_id": int(knowledge_id)})
    except Exception:
        pass


def search_knowledge(query: str, k: int = 4) -> list:
    """相似度检索知识片段。"""
    try:
        docs = get_store().similarity_search(query, k=k)
    except Exception:
        return []
    results = []
    for doc in docs:
        results.append({
            "knowledge_id": doc.metadata.get("knowledge_id"),
            "title": doc.metadata.get("title", ""),
            "category": doc.metadata.get("category", ""),
            "content": doc.page_content,
        })
    return results


def vectorize_row(db, row: Knowledge) -> str:
    """向量化单条知识，失败时保留原文并记录状态。"""
    try:
        count = upsert_knowledge(row.id, row.title, row.category, row.content)
        row.vector_status = "已向量化"
        row.chunk_count = count
        db.commit()
        return ""
    except Exception as exc:
        row.vector_status = "未向量化"
        row.chunk_count = 0
        db.commit()
        return str(exc)


def sync_if_empty(db):
    """向量库为空时，把数据库中的知识同步进去。"""
    try:
        count = get_store()._collection.count()
    except Exception:
        count = 0
    if count:
        return
    for row in db.query(Knowledge).all():
        error = vectorize_row(db, row)
        if error:
            print(f"知识[{row.id}]向量化失败：{error}")


def rebuild_all(db) -> dict:
    """清空向量库后，重新索引全部知识。"""
    reset_store()
    success = 0
    failed = 0
    for row in db.query(Knowledge).all():
        error = vectorize_row(db, row)
        if error:
            failed += 1
        else:
            success += 1
    return {"success": success, "failed": failed}
