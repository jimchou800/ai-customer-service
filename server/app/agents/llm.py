"""大模型与嵌入模型客户端。"""
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app.core.config import settings

_llm_cache = {}
_embeddings = None


def get_llm(temperature: float = 0.3, streaming: bool = True) -> ChatOpenAI:
    """获取聊天模型，模型名为 qwen3.8-27b。"""
    key = (temperature, streaming)
    if key not in _llm_cache:
        _llm_cache[key] = ChatOpenAI(
            model=settings.CHAT_MODEL,
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            temperature=temperature,
            timeout=90,
            max_retries=1,
            streaming=streaming,
            extra_body={"enable_thinking": False},
        )
    return _llm_cache[key]


def get_embeddings() -> OpenAIEmbeddings:
    """获取嵌入模型，使用 text-embedding-v4，维度 2048。"""
    global _embeddings
    if _embeddings is None:
        _embeddings = OpenAIEmbeddings(
            model=settings.EMBED_MODEL,
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            dimensions=settings.EMBED_DIMENSIONS,
            check_embedding_ctx_length=False,
            chunk_size=10,
        )
    return _embeddings
