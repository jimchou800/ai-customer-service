"""登录令牌与权限依赖。"""
from datetime import datetime, timedelta

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.entities import User

bearer_scheme = HTTPBearer(auto_error=False)


def create_token(user_id: int, role: str) -> str:
    """生成 JWT 登录令牌。"""
    payload = {
        "uid": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRE_HOURS),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """解析令牌并返回当前登录用户。"""
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=401, detail="请先登录")
    try:
        payload = jwt.decode(credentials.credentials, settings.JWT_SECRET, algorithms=["HS256"])
    except Exception:
        raise HTTPException(status_code=401, detail="登录已失效，请重新登录")
    user = db.get(User, payload.get("uid"))
    if user is None or user.status != 1:
        raise HTTPException(status_code=401, detail="账号不可用")
    return user


def get_admin(user: User = Depends(get_current_user)) -> User:
    """要求当前用户为管理员。"""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user
