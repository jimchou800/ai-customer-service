"""通用图片上传。"""
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.core.files import IMAGE_EXTS, save_upload
from app.core.response import ok
from app.core.security import get_current_user
from app.models.entities import User

router = APIRouter(prefix="/upload", tags=["上传"])


@router.post("/image")
def upload_image(
    folder: str = Form("chat"),
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    """上传图片到指定目录，商品图仅管理员可用。"""
    if folder not in ("avatar", "product", "chat"):
        raise HTTPException(status_code=400, detail="上传目录不正确")
    if folder == "product" and user.role != "admin":
        raise HTTPException(status_code=403, detail="没有权限")
    url = save_upload(file, folder, IMAGE_EXTS)
    return ok({"url": url})
