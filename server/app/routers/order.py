"""订单管理。"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import ok, page_data, paginate
from app.core.security import get_admin
from app.models.entities import Order, OrderItem, User
from app.schemas.schemas import OrderStatusForm, ShipForm, item_dict, order_dict

router = APIRouter(prefix="/orders", tags=["订单"])
ORDER_STATUS = {"待付款", "待发货", "已发货", "已完成", "已取消", "退款中"}


def _detail(db: Session, row: Order, nickname: str = "") -> dict:
    """组装订单和明细。"""
    items = db.query(OrderItem).filter(OrderItem.order_id == row.id).all()
    return order_dict(row, nickname, [item_dict(item) for item in items])


@router.get("")
def list_orders(
    page: int = 1,
    page_size: int = 10,
    keyword: str = "",
    status: str = "",
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin),
):
    """分页查询订单，可按订单号、用户和状态筛选。"""
    query = db.query(Order, User.nickname).join(User, User.id == Order.user_id)
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(or_(Order.order_no.like(like), User.nickname.like(like), User.username.like(like)))
    if status:
        query = query.filter(Order.status == status)
    query = query.order_by(Order.id.desc())
    total, rows = paginate(query, page, page_size)
    return ok(page_data([_detail(db, row, nickname) for row, nickname in rows], total))


@router.get("/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db), admin: User = Depends(get_admin)):
    """查看订单详情。"""
    row = db.get(Order, order_id)
    if row is None:
        raise HTTPException(status_code=404, detail="订单不存在")
    user = db.get(User, row.user_id)
    return ok(_detail(db, row, user.nickname if user else ""))


@router.put("/{order_id}/ship")
def ship_order(order_id: int, form: ShipForm, db: Session = Depends(get_db), admin: User = Depends(get_admin)):
    """填写物流公司与单号并发货。"""
    row = db.get(Order, order_id)
    if row is None:
        raise HTTPException(status_code=404, detail="订单不存在")
    if row.status not in ("待发货", "已发货"):
        raise HTTPException(status_code=400, detail="当前状态不能发货")
    row.logistics_company = form.logistics_company
    row.logistics_no = form.logistics_no
    row.status = "已发货"
    if row.ship_time is None:
        row.ship_time = datetime.now()
    db.commit()
    user = db.get(User, row.user_id)
    return ok(_detail(db, row, user.nickname if user else ""), "已发货")


@router.put("/{order_id}/status")
def update_status(order_id: int, form: OrderStatusForm, db: Session = Depends(get_db), admin: User = Depends(get_admin)):
    """修改订单状态，并补齐对应时间。"""
    if form.status not in ORDER_STATUS:
        raise HTTPException(status_code=400, detail="订单状态不正确")
    row = db.get(Order, order_id)
    if row is None:
        raise HTTPException(status_code=404, detail="订单不存在")
    now = datetime.now()
    row.status = form.status
    if form.status in ("待发货", "已发货", "已完成", "退款中") and row.pay_time is None:
        row.pay_time = now
    if form.status in ("已发货", "已完成") and row.ship_time is None:
        row.ship_time = now
    if form.status == "已完成" and row.finish_time is None:
        row.finish_time = now
    db.commit()
    user = db.get(User, row.user_id)
    return ok(_detail(db, row, user.nickname if user else ""), "状态已更新")
