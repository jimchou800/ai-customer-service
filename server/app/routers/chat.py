"""智能客服会话与流式问答。"""
import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessage, HumanMessage
from sqlalchemy.orm import Session

from app.agents.graph import get_graph
from app.agents.state import to_data_url
from app.core.database import SessionLocal, get_db
from app.core.response import ok
from app.core.security import get_current_user
from app.models.entities import ChatMessage, ChatSession, User
from app.schemas.schemas import ChatSendForm, format_time

router = APIRouter(prefix="/chat", tags=["智能客服"])


def parse_json(value: str):
    """把文本 JSON 还原为列表。"""
    if not value:
        return []
    try:
        data = json.loads(value)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def session_dict(row: ChatSession, user: User = None) -> dict:
    """会话转字典。"""
    return {
        "id": row.id,
        "user_id": row.user_id,
        "username": user.username if user else "",
        "nickname": user.nickname if user else "",
        "title": row.title,
        "create_time": format_time(row.create_time),
        "update_time": format_time(row.update_time),
    }


def message_dict(row: ChatMessage) -> dict:
    """消息转字典。"""
    return {
        "id": row.id,
        "session_id": row.session_id,
        "role": row.role,
        "content": row.content or "",
        "images": parse_json(row.images),
        "intent": row.intent or "",
        "agent_name": row.agent_name or "",
        "sources": parse_json(row.sources),
        "create_time": format_time(row.create_time),
    }


def get_owned_session(db: Session, session_id: int, user: User) -> ChatSession:
    """获取会话，普通用户只能访问自己的会话。"""
    row = db.get(ChatSession, session_id)
    if row is None:
        raise HTTPException(status_code=404, detail="会话不存在")
    if user.role != "admin" and row.user_id != user.id:
        raise HTTPException(status_code=403, detail="无权访问该会话")
    return row


def sse(payload: dict) -> str:
    """编码一条服务器推送事件。"""
    return "data: " + json.dumps(payload, ensure_ascii=False) + "\n\n"


def chunk_text(text: str, size: int = 12):
    """把完整回答切成小段，便于前端逐段显示。"""
    for index in range(0, len(text), size):
        yield text[index:index + size]


def build_messages(rows, current_id: int):
    """把历史消息转成模型消息，当前消息保留图片。"""
    messages = []
    for row in rows:
        if row.role == "user":
            images = parse_json(row.images)
            text = row.content or ""
            if row.id == current_id and images:
                content = [{"type": "text", "text": text or "请识别这张图片并结合电商售后场景协助处理"}]
                for url in images:
                    try:
                        content.append({"type": "image_url", "image_url": {"url": to_data_url(url)}})
                    except Exception:
                        content[0]["text"] += "\n（有一张图片暂时无法读取）"
                messages.append(HumanMessage(content=content))
            else:
                if images:
                    text = (text + "\n（用户发送了图片）").strip()
                messages.append(HumanMessage(content=text or "（空消息）"))
        else:
            messages.append(AIMessage(content=row.content or ""))
    return messages


@router.get("/sessions")
def list_sessions(scope: str = "mine", db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """查询我的会话；管理员可查看全部用户会话。"""
    query = db.query(ChatSession)
    if scope == "all":
        if user.role != "admin":
            raise HTTPException(status_code=403, detail="需要管理员权限")
    else:
        query = query.filter(ChatSession.user_id == user.id)
    rows = query.order_by(ChatSession.update_time.desc(), ChatSession.id.desc()).all()
    users = {item.id: item for item in db.query(User).filter(User.id.in_([row.user_id for row in rows] or [0])).all()}
    return ok([session_dict(row, users.get(row.user_id)) for row in rows])


@router.post("/sessions")
def create_session(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """创建一个新的客服会话。"""
    now = datetime.now()
    row = ChatSession(user_id=user.id, title="新的会话", create_time=now, update_time=now)
    db.add(row)
    db.commit()
    db.refresh(row)
    return ok(session_dict(row, user))


@router.delete("/sessions/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """删除会话及其消息。"""
    row = get_owned_session(db, session_id, user)
    db.query(ChatMessage).filter(ChatMessage.session_id == row.id).delete()
    db.delete(row)
    db.commit()
    return ok(msg="会话已删除")


@router.get("/sessions/{session_id}/messages")
def list_messages(session_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """读取会话消息。"""
    row = get_owned_session(db, session_id, user)
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == row.id).order_by(ChatMessage.id.asc()).all()
    return ok([message_dict(item) for item in messages])


@router.post("/sessions/{session_id}/stream")
def stream_chat(session_id: int, form: ChatSendForm, user: User = Depends(get_current_user)):
    """保存用户消息，并通过 LangGraph 流式返回客服回复。"""
    db = SessionLocal()
    try:
        session = get_owned_session(db, session_id, user)
        content = (form.content or "").strip()
        image_urls = [url for url in (form.image_urls or []) if url][:3]
        if not content and not image_urls:
            raise HTTPException(status_code=400, detail="请输入内容或上传图片")
        now = datetime.now()
        user_message = ChatMessage(
            session_id=session.id,
            role="user",
            content=content,
            images=json.dumps(image_urls, ensure_ascii=False),
            intent="",
            agent_name="",
            sources="",
            create_time=now,
        )
        db.add(user_message)
        if session.title in ("新的会话", ""):
            session.title = (content or "图片咨询")[:24]
        session.update_time = now
        db.commit()
        db.refresh(user_message)
        history = db.query(ChatMessage).filter(ChatMessage.session_id == session.id).order_by(ChatMessage.id.asc()).all()
        history = history[-8:]
        state = {
            "messages": build_messages(history, user_message.id),
            "intent": "",
            "user_id": session.user_id,
            "session_id": session.id,
            "image_urls": image_urls,
            "agent_name": "",
            "answer": "",
            "sources": [],
            "ticket_no": "",
        }
    except Exception:
        db.close()
        raise

    def generate():
        """推送意图、回答片段、引用来源和结束事件。"""
        answer = ""
        intent = ""
        agent_name = ""
        sources = []
        ticket_no = ""
        streamed = False
        saved = False
        try:
            graph = get_graph()
            try:
                iterator = graph.stream(state, stream_mode=["updates", "messages"], config={"recursion_limit": 16})
            except TypeError:
                iterator = (("updates", item) for item in graph.stream(state, config={"recursion_limit": 16}))
            for mode, payload in iterator:
                if mode == "updates":
                    updates = payload if isinstance(payload, dict) else {}
                    for node, upd in updates.items():
                        if not isinstance(upd, dict):
                            continue
                        if node == "router" and upd.get("intent"):
                            intent = upd["intent"]
                            yield sse({"type": "intent", "intent": intent})
                        if upd.get("agent_name"):
                            agent_name = upd["agent_name"]
                            yield sse({"type": "agent", "agent": agent_name, "intent": upd.get("intent") or intent})
                        if node == "knowledge" and upd.get("sources") is not None:
                            sources = upd.get("sources") or []
                            yield sse({"type": "sources", "sources": sources})
                        if upd.get("ticket_no"):
                            ticket_no = upd["ticket_no"]
                            yield sse({"type": "ticket", "ticket_no": ticket_no})
                        if upd.get("answer"):
                            answer = upd["answer"]
                            if node in ("tool", "ticket") or not streamed:
                                for piece in chunk_text(answer):
                                    yield sse({"type": "delta", "content": piece})
                                streamed = True
                elif mode == "messages":
                    chunk = payload[0] if isinstance(payload, tuple) else payload
                    meta = payload[1] if isinstance(payload, tuple) and len(payload) > 1 else {}
                    node = meta.get("langgraph_node", "") if isinstance(meta, dict) else ""
                    # 只转发增量片段，避免最终完整消息再追加一次
                    if getattr(chunk, "type", "") != "AIMessageChunk":
                        continue
                    if node not in ("knowledge", "chitchat"):
                        continue
                    if getattr(chunk, "tool_call_chunks", None):
                        continue
                    text = chunk.content if isinstance(getattr(chunk, "content", ""), str) else ""
                    if isinstance(chunk.content, list):
                        text = "".join(item.get("text", "") for item in chunk.content if isinstance(item, dict))
                    if text:
                        streamed = True
                        yield sse({"type": "delta", "content": text})
            if not answer:
                answer = "抱歉，我暂时没有生成有效回复，请换个方式描述或转为工单。"
                yield sse({"type": "delta", "content": answer})
            assistant = ChatMessage(
                session_id=session.id,
                role="assistant",
                content=answer,
                images="",
                intent=intent,
                agent_name=agent_name,
                sources=json.dumps(sources, ensure_ascii=False),
                create_time=datetime.now(),
            )
            session.update_time = datetime.now()
            db.add(assistant)
            db.commit()
            saved = True
            yield sse({
                "type": "done",
                "answer": answer,
                "intent": intent,
                "agent": agent_name,
                "sources": sources,
                "ticket_no": ticket_no,
                "message_id": assistant.id,
            })
        except Exception as exc:
            db.rollback()
            yield sse({"type": "error", "message": f"客服处理失败：{exc}"})
        finally:
            if not saved:
                db.rollback()
            db.close()

    return StreamingResponse(generate(), media_type="text/event-stream", headers={
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
    })
