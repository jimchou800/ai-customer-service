"""多智能体之间传递的状态与文本工具。"""
import base64
import mimetypes
from typing import Annotated

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from app.core.files import resolve_upload


class AgentState(TypedDict):
    """LangGraph 状态。"""

    messages: Annotated[list, add_messages]
    intent: str
    user_id: int
    session_id: int
    image_urls: list
    agent_name: str
    answer: str
    sources: list
    ticket_no: str


def text_of(content) -> str:
    """从字符串或多模态内容中提取纯文本。"""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text") or "")
            else:
                text = getattr(item, "text", None)
                if text:
                    parts.append(text)
        return "".join(parts)
    return str(content)


def last_user_text(state: AgentState) -> str:
    """取最近一条用户消息的文本。"""
    for message in reversed(state.get("messages") or []):
        if getattr(message, "type", "") == "human":
            return text_of(message.content)
    return ""


def to_data_url(url: str) -> str:
    """把上传图片转成模型可识别的 data URL。"""
    path = resolve_upload(url)
    mime = mimetypes.guess_type(path)[0] or "image/jpeg"
    with open(path, "rb") as handle:
        encoded = base64.b64encode(handle.read()).decode()
    return f"data:{mime};base64,{encoded}"
