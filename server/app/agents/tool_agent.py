"""订单、物流和商品工具智能体。"""
from contextvars import ContextVar

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool

from app.agents.llm import get_llm
from app.agents.state import AgentState, last_user_text, text_of
from app.core.database import SessionLocal
from app.models.entities import Order, OrderItem, Product, User

current_user_id: ContextVar[int] = ContextVar("current_user_id", default=0)

TOOL_PROMPT = """你是电商智能客服的业务办理专员。用户询问订单、物流、商品或取消订单时，必须调用工具，不要编造订单号、金额和物流单号。
回答使用简洁中文。取消订单只允许待付款和待发货。如果工具没有查到数据，要如实说明。"""


def _user_orders(db, user_id: int):
    """当前用户的订单查询。"""
    return db.query(Order).filter(Order.user_id == user_id)


def _item_names(db, order_id: int) -> str:
    """拼接订单商品名称。"""
    rows = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    return "、".join(f"{row.product_name} x{row.quantity}" for row in rows) or "无商品明细"


@tool
def query_my_orders() -> str:
    """查询当前登录用户最近的订单，包括订单号、状态、金额、时间和商品。"""
    user_id = current_user_id.get()
    db = SessionLocal()
    try:
        rows = _user_orders(db, user_id).order_by(Order.id.desc()).limit(8).all()
        if not rows:
            return "当前账号还没有订单。"
        lines = ["您最近的订单如下："]
        for row in rows:
            created = row.create_time.strftime("%Y-%m-%d %H:%M:%S") if row.create_time else ""
            lines.append(
                f"订单号 {row.order_no}，状态 {row.status}，金额 {float(row.total_amount):.2f} 元，"
                f"下单时间 {created}，商品：{_item_names(db, row.id)}"
            )
        return "\n".join(lines)
    finally:
        db.close()


@tool
def query_order_detail(order_no: str) -> str:
    """根据订单号查询当前用户的订单详情。参数 order_no 是订单号。"""
    user_id = current_user_id.get()
    db = SessionLocal()
    try:
        row = _user_orders(db, user_id).filter(Order.order_no == order_no).first()
        if row is None:
            return f"没有找到属于您的订单 {order_no}。"
        created = row.create_time.strftime("%Y-%m-%d %H:%M:%S") if row.create_time else ""
        return (
            f"订单号 {row.order_no}，状态 {row.status}，金额 {float(row.total_amount):.2f} 元，"
            f"支付方式 {row.pay_method or '未支付'}，收货人 {row.receiver}，电话 {row.phone}，"
            f"地址 {row.address}，下单时间 {created}，商品：{_item_names(db, row.id)}。"
        )
    finally:
        db.close()


@tool
def query_logistics(order_no: str) -> str:
    """根据订单号查询当前用户的物流信息。参数 order_no 是订单号。"""
    user_id = current_user_id.get()
    db = SessionLocal()
    try:
        row = _user_orders(db, user_id).filter(Order.order_no == order_no).first()
        if row is None:
            return f"没有找到属于您的订单 {order_no}。"
        if not row.logistics_no:
            return f"订单 {row.order_no} 当前状态为 {row.status}，暂时还没有物流单号。"
        ship = row.ship_time.strftime("%Y-%m-%d %H:%M:%S") if row.ship_time else ""
        return (
            f"订单 {row.order_no} 由 {row.logistics_company} 承运，运单号 {row.logistics_no}，"
            f"发货时间 {ship}，当前订单状态 {row.status}。"
        )
    finally:
        db.close()


@tool
def search_products(keyword: str) -> str:
    """按名称或分类搜索在售商品。参数 keyword 是关键词。"""
    db = SessionLocal()
    try:
        like = f"%{keyword.strip()}%"
        rows = db.query(Product).filter(
            Product.status == 1,
            (Product.name.like(like)) | (Product.category.like(like)) | (Product.description.like(like)),
        ).limit(8).all()
        if not rows:
            return f"没有找到与“{keyword}”相关的在售商品。"
        lines = ["为您找到以下在售商品："]
        for row in rows:
            lines.append(f"{row.name}，分类 {row.category}，单价 {float(row.price):.2f} 元，库存 {row.stock}。{row.description or ''}")
        return "\n".join(lines)
    finally:
        db.close()


@tool
def cancel_order(order_no: str) -> str:
    """取消当前用户的订单。仅待付款和待发货可以取消。参数 order_no 是订单号。"""
    user_id = current_user_id.get()
    db = SessionLocal()
    try:
        row = _user_orders(db, user_id).filter(Order.order_no == order_no).first()
        if row is None:
            return f"没有找到属于您的订单 {order_no}。"
        if row.status not in ("待付款", "待发货"):
            return f"订单 {order_no} 当前状态为 {row.status}，不能直接取消。如需退货或退款，请转为工单处理。"
        row.status = "已取消"
        db.commit()
        return f"订单 {order_no} 已取消。"
    finally:
        db.close()


TOOLS = [query_my_orders, query_order_detail, query_logistics, search_products, cancel_order]
_agent = None


def get_tool_agent():
    """创建可调用工具的 ReAct 智能体。"""
    global _agent
    if _agent is None:
        from langgraph.prebuilt import create_react_agent

        llm = get_llm(0.2, True)
        try:
            _agent = create_react_agent(llm, TOOLS, prompt=TOOL_PROMPT)
        except TypeError:
            _agent = create_react_agent(llm, TOOLS, state_modifier=TOOL_PROMPT)
    return _agent


def _fallback(text: str) -> str:
    """工具模型不可用时，按关键词直接调用工具。"""
    import re

    matched = re.search(r"DD\d+", text.upper())
    order_no = matched.group() if matched else ""
    if "取消" in text and order_no:
        return cancel_order.invoke({"order_no": order_no})
    if any(word in text for word in ("物流", "快递", "运单")) and order_no:
        return query_logistics.invoke({"order_no": order_no})
    if "订单" in text and order_no:
        return query_order_detail.invoke({"order_no": order_no})
    if any(word in text for word in ("商品", "耳机", "手表", "搜索", "有没有", "推荐")):
        keyword = text.replace("帮我", "").replace("搜索", "").strip()[:20] or "数码"
        return search_products.invoke({"keyword": keyword})
    return query_my_orders.invoke({})


def tool_node(state: AgentState) -> dict:
    """调用订单、物流、商品工具后生成回复。"""
    token = current_user_id.set(state["user_id"])
    try:
        db = SessionLocal()
        try:
            user = db.get(User, state["user_id"])
            nickname = user.nickname if user else "用户"
        finally:
            db.close()
        try:
            result = get_tool_agent().invoke(
                {"messages": [HumanMessage(content=f"当前用户是{nickname}。"), *state["messages"]]},
                config={"recursion_limit": 10},
            )
            answer = ""
            for message in reversed(result.get("messages") or []):
                content = text_of(getattr(message, "content", ""))
                if getattr(message, "type", "") == "ai" and content and not getattr(message, "tool_calls", None):
                    answer = content.strip()
                    break
            if not answer:
                answer = _fallback(last_user_text(state))
        except Exception as exc:
            print(f"工具智能体失败，改用直接查询：{exc}")
            answer = _fallback(last_user_text(state))
        return {
            "messages": [AIMessage(content=answer)],
            "answer": answer,
            "agent_name": "工具客服",
            "intent": "tool",
            "sources": [],
        }
    finally:
        current_user_id.reset(token)
