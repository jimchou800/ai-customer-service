"""知识库检索问答智能体。"""
from langchain_core.messages import AIMessage, SystemMessage

from app.agents.llm import get_llm
from app.agents.state import AgentState, last_user_text, text_of
from app.rag.vector_store import search_knowledge


def knowledge_node(state: AgentState) -> dict:
    """检索 Chroma 知识库后，依据资料回答。"""
    query = last_user_text(state) or "请结合图片回答电商售后问题"
    docs = search_knowledge(query, k=4)
    if docs:
        context = "\n\n".join(
            f"【{item['category']}｜{item['title']}】\n{item['content']}" for item in docs
        )
    else:
        context = "当前没有检索到相关资料。"
    prompt = (
        "你是电商智能客服的知识库专员。请只用下面的资料回答，不要编造政策数字。"
        "语气亲切、专业，使用中文。资料不足时要明确说明，并建议用户转人工工单。\n\n"
        f"资料：\n{context}"
    )
    response = get_llm(0.2, True).invoke([SystemMessage(content=prompt), *state["messages"]])
    answer = text_of(response.content).strip() or "暂时没有查询到对应政策，您可以补充问题，或让我为您创建工单。"
    sources = [
        {"title": item["title"], "category": item["category"], "knowledge_id": item["knowledge_id"]}
        for item in docs
    ]
    return {
        "messages": [AIMessage(content=answer)],
        "answer": answer,
        "sources": sources,
        "agent_name": "知识库客服",
        "intent": "knowledge",
    }
