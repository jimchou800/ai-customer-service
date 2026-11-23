"""工单管理。"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import ok, page_data, paginate
from app.core.security import get_admin
from app.models.entities import Ticket, User
from app.schemas.schemas import TicketHandleForm, format_time

router = APIRouter(prefix="/tickets", tags=["工单"])
TICKET_STATUS = {"待处理", "处理中", "已解决", "已关闭"}


def ticket_dict(row: Ticket, nickname: str = "", handler: str = "") -> dict:
    """工单对象转字典。"""
    return {
        "id": row.id,
        "ticket_no": row.ticket_no,
        "user_id": row.user_id,
        "nickname": nickname,
        "session_id": row.session_id,
        "title": row.title,
        "content": row.content,
        "category": row.category,
        "priority": row.priority,
        "status": row.status,
        "reply": row.reply or "",
        "handler_name": handler,
        "create_time": format_time(row.create_time),
        "update_time": format_time(row.update_time),
    }


@router.get("")
def list_tickets(
    page: int = 1,
    page_size: int = 10,
    keyword: str = "",
    status: str = "",
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin),
):
    """分页查询工单。"""
    query = db.query(Ticket, User.nickname).join(User, User.id == Ticket.user_id)
    if keyword:
        like = f"%{keyword}%"
        query = query.filter((Ticket.ticket_no.like(like)) | (Ticket.title.like(like)) | (User.nickname.like(like)))
    if status:
        query = query.filter(Ticket.status == status)
    query = query.order_by(Ticket.id.desc())
    total, rows = paginate(query, page, page_size)
    result = []
    for row, nickname in rows:
        handler_name = ""
        if row.handler_id:
            handler = db.get(User, row.handler_id)
            handler_name = handler.nickname if handler else ""
        result.append(ticket_dict(row, nickname, handler_name))
    return ok(page_data(result, total))


@router.put("/{ticket_id}")
def handle_ticket(
    ticket_id: int,
    form: TicketHandleForm,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin),
):
    """回复工单并流转状态。"""
    if form.status not in TICKET_STATUS:
        raise HTTPException(status_code=400, detail="工单状态不正确")
    row = db.get(Ticket, ticket_id)
    if row is None:
        raise HTTPException(status_code=404, detail="工单不存在")
    row.status = form.status
    row.reply = form.reply
    row.handler_id = admin.id
    row.update_time = datetime.now()
    db.commit()
    db.refresh(row)
    user = db.get(User, row.user_id)
    return ok(ticket_dict(row, user.nickname if user else "", admin.nickname), "工单已更新")
