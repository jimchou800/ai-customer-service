"""上传文件保存与文档解析。"""
import os
import uuid

from fastapi import HTTPException, UploadFile

from app.core.config import settings

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg"}
DOC_EXTS = {".txt", ".md", ".pdf", ".docx"}
MAX_SIZE = 8 * 1024 * 1024


def ensure_upload_dirs():
    """确保上传根目录及分类子目录存在。"""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    for folder in ("avatar", "product", "chat", "knowledge"):
        os.makedirs(os.path.join(settings.UPLOAD_DIR, folder), exist_ok=True)


def save_upload(file: UploadFile, folder: str, allowed: set) -> str:
    """保存上传文件并返回可访问的相对地址。"""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail="不支持的文件类型")
    content = file.file.read()
    if not content:
        raise HTTPException(status_code=400, detail="文件为空")
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="文件不能超过8MB")
    ensure_upload_dirs()
    filename = uuid.uuid4().hex + ext
    path = os.path.join(settings.UPLOAD_DIR, folder, filename)
    with open(path, "wb") as handle:
        handle.write(content)
    return f"/uploads/{folder}/{filename}"


def resolve_upload(url: str) -> str:
    """把 /uploads 地址转换成磁盘路径，并阻止目录穿越。"""
    if not url or not url.startswith("/uploads/"):
        raise HTTPException(status_code=400, detail="非法文件地址")
    relative = url[len("/uploads/"):].replace("\\", "/")
    if ".." in relative.split("/"):
        raise HTTPException(status_code=400, detail="非法文件地址")
    root = os.path.normpath(settings.UPLOAD_DIR)
    path = os.path.normpath(os.path.join(root, relative.replace("/", os.sep)))
    if path != root and not path.startswith(root + os.sep):
        raise HTTPException(status_code=400, detail="非法文件地址")
    return path


def read_document(path: str) -> str:
    """按扩展名读取 txt、md、pdf、docx 文本。"""
    ext = os.path.splitext(path)[1].lower()
    if ext in {".txt", ".md"}:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    if ext == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(path)
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    if ext == ".docx":
        from docx import Document

        document = Document(path)
        return "\n".join(paragraph.text for paragraph in document.paragraphs)
    raise HTTPException(status_code=400, detail="暂不支持该文档类型")
