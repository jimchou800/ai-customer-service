"""意图识别路由智能体。"""
import json
import re
from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

from app.agents.llm import get_llm
from app.agents.state import AgentState, last_user_text, text_of

INTENTS = {"knowledge", "tool", "ticket", "chitchat"}

ROUTER_PROMPT = """你是电商智能客服的意图路由器。请结合用户文字和图片，只输出 JSON：
{"intent":"knowledge|tool|ticket|chitchat","reason":"简短原因"}
判定规则：
- knowledge：优惠政策、优惠券、积分、售后、质保、退货、退款、物流政策、支付方式、账户安全、配送说明等规则咨询。
- tool：查询订单、查询物流、搜索商品、取消订单等需要读取系统数据的请求。
- ticket：投诉、要求人工、商品破损、质量纠纷、退款异常升级、图片明显显示商品损坏。
- chitchat：问候、感谢、身份询问或其他闲聊。
如果同时涉及政策和具体订单查询，优先 tool；如果用户明确抱怨、投诉或图片显示破损，优先 ticket。"""


class IntentResult(BaseModel):
    """路由结果。"""

    intent: Literal["knowledge", "tool", "ticket", "chitchat"]
    reason: str = ""


def keyword_intent(text: str, has_image: bool) -> str:
    """模型不可用时的关键词兜底。"""
    if any(word in text for word in ("工单", "投诉", "人工", "破损", "坏了", "质量问题", "裂了")):
        return "ticket"
    if has_image and any(word in text for word in ("坏", "破", "损", "退")):
        return "ticket"
    if any(word in text for word in ("订单", "物流", "快递", "发货", "取消", "单号")):
        return "tool"
    if any(word in text for word in ("你好", "您好", "谢谢", "再见", "你是谁", "在吗")):
        return "chitchat"
    return "knowledge"


def _parse_intent(raw: str) -> str:
    """从模型文本中解析意图。"""
    match = re.search(r"\{.*\}", raw or "", re.S)
    if not match:
        return ""
    try:
        data = json.loads(match.group())
    except Exception:
        return ""
    intent = data.get("intent", "")
    return intent if intent in INTENTS else ""


def router_node(state: AgentState) -> dict:
    """识别用户意图，决定后续交给哪个智能体。"""
    text = last_user_text(state)
    has_image = bool(state.get("image_urls"))
    intent = ""
    try:
        llm = get_llm(temperature=0, streaming=False)
        last = state["messages"][-1]
        try:
            result = llm.with_structured_output(IntentResult).invoke([
                SystemMessage(content=ROUTER_PROMPT),
                last if getattr(last, "type", "") == "human" else HumanMessage(content=text or "请查看图片"),
            ])
            intent = result.intent
        except Exception:
            response = llm.invoke([
                SystemMessage(content=ROUTER_PROMPT),
                last if getattr(last, "type", "") == "human" else HumanMessage(content=text or "请查看图片"),
            ])
            intent = _parse_intent(text_of(response.content))
    except Exception as exc:
        print(f"意图识别失败，改用关键词：{exc}")
    if intent not in INTENTS:
        intent = keyword_intent(text, has_image)
    return {"intent": intent}
