"""闲聊与通用接待智能体。"""
from langchain_core.messages import AIMessage, SystemMessage

from app.agents.llm import get_llm
from app.agents.state import AgentState, text_of

CHAT_PROMPT = """你是“基于LangGraph的AI智能电商客服系统”的接待专员。
请用亲切的中文简短回复问候、感谢和身份询问。
可以告诉用户你能咨询优惠积分售后物流政策、查询订单物流商品、识别图片，以及把复杂问题升级为工单。
不要编造订单和退款结果。"""


def chat_node(state: AgentState) -> dict:
    """处理寒暄和通用问题。"""
    try:
        response = get_llm(0.5, True).invoke([SystemMessage(content=CHAT_PROMPT), *state["messages"]])
        answer = text_of(response.content).strip()
    except Exception as exc:
        print(f"闲聊模型失败：{exc}")
        answer = ""
    if not answer:
        answer = "您好，我是智能电商客服。您可以咨询退货、积分和物流政策，也可以让我查询订单，或把问题升级为工单。"
    return {
        "messages": [AIMessage(content=answer)],
        "answer": answer,
        "agent_name": "闲聊客服",
        "intent": "chitchat",
        "sources": [],
    }
