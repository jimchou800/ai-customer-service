"""组装 LangGraph 多代理流程图。"""
from langgraph.graph import END, StateGraph

from app.agents.chat_agent import chat_node
from app.agents.knowledge_agent import knowledge_node
from app.agents.router_agent import router_node
from app.agents.state import AgentState
from app.agents.ticket_agent import ticket_node
from app.agents.tool_agent import tool_node

_graph = None


def route_intent(state: AgentState) -> str:
    """按识别出的意图选择下一个节点。"""
    intent = state.get("intent") or "chitchat"
    if intent not in {"knowledge", "tool", "ticket", "chitchat"}:
        return "chitchat"
    return intent


def build_graph():
    """构建 Router 分发到知识库、工具、工单和闲聊的状态图。"""
    graph = StateGraph(AgentState)
    graph.add_node("router", router_node)
    graph.add_node("knowledge", knowledge_node)
    graph.add_node("tool", tool_node)
    graph.add_node("ticket", ticket_node)
    graph.add_node("chitchat", chat_node)
    graph.set_entry_point("router")
    graph.add_conditional_edges("router", route_intent, {
        "knowledge": "knowledge",
        "tool": "tool",
        "ticket": "ticket",
        "chitchat": "chitchat",
    })
    graph.add_edge("knowledge", END)
    graph.add_edge("tool", END)
    graph.add_edge("ticket", END)
    graph.add_edge("chitchat", END)
    return graph.compile()


def get_graph():
    """返回编译后的图，避免重复编译。"""
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph
