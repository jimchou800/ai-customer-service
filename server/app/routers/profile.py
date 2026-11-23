"""个人中心。"""
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.files import IMAGE_EXTS, save_upload
from app.core.response import ok
from app.core.security import get_current_user
from app.models.entities import User
from app.schemas.schemas import PasswordForm, ProfileForm, user_dict

router = APIRouter(prefix="/profile", tags=["个人中心"])


@router.put("")
def update_profile(form: ProfileForm, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """修改昵称、性别、手机号和邮箱。"""
    user.nickname = form.nickname
    user.gender = form.gender
    user.phone = form.phone
    user.email = form.email
    user.update_time = datetime.now()
    db.commit()
    db.refresh(user)
    return ok(user_dict(user), "资料已更新")


@router.post("/avatar")
def update_avatar(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """上传并更换头像。"""
    user.avatar = save_upload(file, "avatar", IMAGE_EXTS)
    user.update_time = datetime.now()
    db.commit()
    db.refresh(user)
    return ok(user_dict(user), "头像已更新")


@router.put("/password")
def update_password(form: PasswordForm, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """校验原密码后修改密码。"""
    if user.password != form.old_password:
        raise HTTPException(status_code=400, detail="原密码不正确")
    user.password = form.new_password
    user.update_time = datetime.now()
    db.commit()
    return ok(msg="密码已修改")
