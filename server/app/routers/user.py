"""用户管理。"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import ok, page_data, paginate
from app.core.security import get_admin
from app.models.entities import User
from app.schemas.schemas import UserSaveForm, user_dict

router = APIRouter(prefix="/users", tags=["用户"])


@router.get("")
def list_users(
    page: int = 1,
    page_size: int = 10,
    keyword: str = "",
    role: str = "",
    status: str = "",
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin),
):
    """分页查询用户。"""
    query = db.query(User)
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(or_(User.username.like(like), User.nickname.like(like), User.phone.like(like)))
    if role:
        query = query.filter(User.role == role)
    if status in ("0", "1"):
        query = query.filter(User.status == int(status))
    query = query.order_by(User.id.desc())
    total, rows = paginate(query, page, page_size)
    return ok(page_data([user_dict(row) for row in rows], total))


@router.post("")
def create_user(form: UserSaveForm, db: Session = Depends(get_db), admin: User = Depends(get_admin)):
    """管理员新增用户，未填密码时默认为 123456。"""
    if db.query(User).filter(User.username == form.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    if form.role not in ("admin", "user"):
        raise HTTPException(status_code=400, detail="角色不正确")
    now = datetime.now()
    row = User(
        username=form.username,
        password=form.password or "123456",
        nickname=form.nickname,
        avatar="",
        gender=form.gender or "男",
        phone=form.phone,
        email=form.email,
        role=form.role,
        status=1 if form.status else 0,
        create_time=now,
        update_time=now,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return ok(user_dict(row), "用户已新增")


@router.put("/{user_id}")
def update_user(user_id: int, form: UserSaveForm, db: Session = Depends(get_db), admin: User = Depends(get_admin)):
    """编辑用户资料、角色和状态。"""
    row = db.get(User, user_id)
    if row is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    exists = db.query(User).filter(User.username == form.username, User.id != user_id).first()
    if exists:
        raise HTTPException(status_code=400, detail="用户名已存在")
    if form.role not in ("admin", "user"):
        raise HTTPException(status_code=400, detail="角色不正确")
    row.username = form.username
    row.nickname = form.nickname
    row.gender = form.gender
    row.phone = form.phone
    row.email = form.email
    row.role = form.role
    row.status = 1 if form.status else 0
    if form.password:
        row.password = form.password
    row.update_time = datetime.now()
    db.commit()
    db.refresh(row)
    return ok(user_dict(row), "用户已更新")


@router.put("/{user_id}/reset-password")
def reset_password(user_id: int, db: Session = Depends(get_db), admin: User = Depends(get_admin)):
    """把用户密码重置为 123456。"""
    row = db.get(User, user_id)
    if row is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    row.password = "123456"
    row.update_time = datetime.now()
    db.commit()
    return ok(msg="密码已重置为123456")


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(get_admin)):
    """删除用户，不能删除当前登录管理员。"""
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="不能删除当前登录账号")
    row = db.get(User, user_id)
    if row is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    db.delete(row)
    db.commit()
    return ok(msg="用户已删除")
