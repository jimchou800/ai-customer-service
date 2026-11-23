"""工单升级智能体。"""
import json
import re
from datetime import datetime

from langchain_core.messages import AIMessage, SystemMessage
from pydantic import BaseModel, Field

from app.agents.llm import get_llm
from app.agents.state import AgentState, last_user_text, text_of
from app.core.database import SessionLocal
from app.models.entities import Ticket

TICKET_CATEGORIES = ["商品问题", "物流问题", "售后问题", "账户问题", "其他"]
PRIORITIES = ["低", "中", "高"]


class TicketDraft(BaseModel):
    """工单摘要。"""

    title: str = Field(description="不超过30字的标题")
    category: str = Field(description="商品问题、物流问题、售后问题、账户问题、其他")
    priority: str = Field(description="低、中、高")
    summary: str = Field(description="问题摘要")


def _new_ticket_no() -> str:
    """生成工单号。"""
    return "GD" + datetime.now().strftime("%Y%m%d%H%M%S")


def _draft_from_text(raw: str) -> TicketDraft:
    """解析模型输出的工单 JSON。"""
    match = re.search(r"\{.*\}", raw or "", re.S)
    data = {}
    if match:
        try:
            data = json.loads(match.group())
        except Exception:
            data = {}
    category = data.get("category") if data.get("category") in TICKET_CATEGORIES else "售后问题"
    priority = data.get("priority") if data.get("priority") in PRIORITIES else "中"
    return TicketDraft(
        title=(data.get("title") or "用户售后问题")[:30],
        category=category,
        priority=priority,
        summary=data.get("summary") or raw or "用户请求人工处理",
    )


def ticket_node(state: AgentState) -> dict:
    """总结问题并创建工单，回复工单号。"""
    text = last_user_text(state) or "用户上传了图片，请求人工处理。"
    prompt = (
        "请把用户问题总结成工单，只输出 JSON："
        '{"title":"标题","category":"商品问题|物流问题|售后问题|账户问题|其他","priority":"低|中|高","summary":"摘要"}。'
        "商品破损、投诉优先级设为高。"
    )
    try:
        llm = get_llm(0, False)
        try:
            draft = llm.with_structured_output(TicketDraft).invoke([
                SystemMessage(content=prompt),
                *state["messages"],
            ])
            if draft.category not in TICKET_CATEGORIES:
                draft.category = "售后问题"
            if draft.priority not in PRIORITIES:
                draft.priority = "中"
        except Exception:
            response = llm.invoke([SystemMessage(content=prompt), *state["messages"]])
            draft = _draft_from_text(text_of(response.content))
    except Exception:
        draft = TicketDraft(title="用户售后问题", category="售后问题", priority="中", summary=text[:200])
    now = datetime.now()
    db = SessionLocal()
    try:
        ticket = Ticket(
            ticket_no=_new_ticket_no(),
            user_id=state["user_id"],
            session_id=state.get("session_id"),
            title=draft.title[:120],
            content=draft.summary,
            category=draft.category,
            priority=draft.priority,
            status="待处理",
            reply="",
            create_time=now,
            update_time=now,
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        ticket_no = ticket.ticket_no
    finally:
        db.close()
    image_tip = "我已记录您上传的图片。" if state.get("image_urls") else ""
    answer = (
        f"已为您创建工单 {ticket_no}，分类为{draft.category}，优先级为{draft.priority}。{image_tip}"
        "客服人员会尽快处理，您也可以继续补充订单号或问题细节。"
    )
    return {
        "messages": [AIMessage(content=answer)],
        "answer": answer,
        "agent_name": "工单客服",
        "intent": "ticket",
        "ticket_no": ticket_no,
        "sources": [],
    }
