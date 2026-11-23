"""管理端统计图表。"""
from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import ok
from app.core.security import get_admin
from app.models.entities import ChatMessage, Knowledge, Order, OrderItem, Product, Ticket, User
from app.schemas.schemas import order_dict

router = APIRouter(prefix="/dashboard", tags=["控制台"])

INTENT_NAMES = {
    "knowledge": "知识咨询",
    "tool": "工具办理",
    "ticket": "升级工单",
    "chitchat": "闲聊接待",
}


@router.get("/overview")
def overview(db: Session = Depends(get_db), admin: User = Depends(get_admin)):
    """汇总卡片、近7日订单、意图分布、工单状态和分类销售额。"""
    today = date.today()
    today_orders = db.query(Order).filter(func.date(Order.create_time) == today, Order.status != "已取消").all()
    cards = {
        "user_count": db.query(User).filter(User.role == "user").count(),
        "product_count": db.query(Product).count(),
        "order_count": db.query(Order).count(),
        "pending_ticket": db.query(Ticket).filter(Ticket.status == "待处理").count(),
        "knowledge_count": db.query(Knowledge).count(),
        "today_order": len(today_orders),
        "today_amount": round(sum(float(item.total_amount or 0) for item in today_orders), 2),
    }
    trend = []
    for offset in range(6, -1, -1):
        day = today - timedelta(days=offset)
        rows = db.query(Order).filter(func.date(Order.create_time) == day, Order.status != "已取消").all()
        trend.append({
            "date": day.strftime("%Y-%m-%d"),
            "count": len(rows),
            "amount": round(sum(float(item.total_amount or 0) for item in rows), 2),
        })
    intent_rows = db.query(ChatMessage.intent, func.count(ChatMessage.id)).filter(
        ChatMessage.role == "assistant",
        ChatMessage.intent != "",
    ).group_by(ChatMessage.intent).all()
    intent_pie = [{"name": INTENT_NAMES.get(name, name), "value": count} for name, count in intent_rows]
    ticket_rows = db.query(Ticket.status, func.count(Ticket.id)).group_by(Ticket.status).all()
    ticket_status = [{"name": name, "value": count} for name, count in ticket_rows]
    sale_rows = db.query(Product.category, func.sum(OrderItem.price * OrderItem.quantity)).join(
        OrderItem, OrderItem.product_id == Product.id
    ).join(Order, Order.id == OrderItem.order_id).filter(Order.status != "已取消").group_by(Product.category).all()
    category_sales = [{"name": name, "value": round(float(amount or 0), 2)} for name, amount in sale_rows]
    recent_rows = db.query(Order, User.nickname).join(User, User.id == Order.user_id).order_by(Order.id.desc()).limit(6).all()
    recent_orders = [order_dict(row, nickname) for row, nickname in recent_rows]
    return ok({
        "cards": cards,
        "order_trend": trend,
        "intent_pie": intent_pie,
        "ticket_status": ticket_status,
        "category_sales": category_sales,
        "recent_orders": recent_orders,
    })
