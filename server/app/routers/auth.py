"""登录与注册。"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import ok
from app.core.security import create_token, get_current_user
from app.models.entities import User
from app.schemas.schemas import LoginForm, RegisterForm, user_dict

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login")
def login(form: LoginForm, db: Session = Depends(get_db)):
    """用户名密码登录，密码按明文比对。"""
    user = db.query(User).filter(User.username == form.username).first()
    if user is None or user.password != form.password:
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    if user.status != 1:
        raise HTTPException(status_code=400, detail="账号已禁用")
    token = create_token(user.id, user.role)
    return ok({"token": token, "user": user_dict(user)})


@router.post("/register")
def register(form: RegisterForm, db: Session = Depends(get_db)):
    """普通用户注册，必须填写确认密码。"""
    exists = db.query(User).filter(User.username == form.username).first()
    if exists:
        raise HTTPException(status_code=400, detail="用户名已存在")
    now = datetime.now()
    user = User(
        username=form.username,
        password=form.password,
        nickname=form.nickname,
        avatar="",
        gender=form.gender or "男",
        phone=form.phone,
        email=form.email,
        role="user",
        status=1,
        create_time=now,
        update_time=now,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_token(user.id, user.role)
    return ok({"token": token, "user": user_dict(user)}, "注册成功")


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    """获取当前登录用户。"""
    return ok(user_dict(user))
