"""知识库管理与向量化。"""
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.files import DOC_EXTS, read_document, resolve_upload, save_upload
from app.core.response import ok, page_data, paginate
from app.core.security import get_admin
from app.models.entities import Knowledge, User
from app.rag.vector_store import delete_knowledge_vectors, rebuild_all, search_knowledge, vectorize_row
from app.schemas.schemas import KnowledgeForm, SearchForm, format_time

router = APIRouter(prefix="/knowledge", tags=["知识库"])


def knowledge_dict(row: Knowledge) -> dict:
    """知识库对象转字典。"""
    return {
        "id": row.id,
        "title": row.title,
        "category": row.category,
        "content": row.content,
        "source_file": row.source_file or "",
        "vector_status": row.vector_status,
        "chunk_count": row.chunk_count or 0,
        "create_time": format_time(row.create_time),
        "update_time": format_time(row.update_time),
    }


@router.get("")
def list_knowledge(
    page: int = 1,
    page_size: int = 10,
    keyword: str = "",
    category: str = "",
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin),
):
    """分页查询知识库。"""
    query = db.query(Knowledge)
    if keyword:
        like = f"%{keyword}%"
        query = query.filter((Knowledge.title.like(like)) | (Knowledge.content.like(like)))
    if category:
        query = query.filter(Knowledge.category == category)
    query = query.order_by(Knowledge.id.desc())
    total, rows = paginate(query, page, page_size)
    return ok(page_data([knowledge_dict(row) for row in rows], total))


@router.post("")
def create_knowledge(form: KnowledgeForm, db: Session = Depends(get_db), admin: User = Depends(get_admin)):
    """新增知识并尝试向量化。"""
    now = datetime.now()
    row = Knowledge(
        title=form.title,
        category=form.category,
        content=form.content,
        source_file=form.source_file,
        vector_status="未向量化",
        chunk_count=0,
        create_time=now,
        update_time=now,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    error = vectorize_row(db, row)
    db.refresh(row)
    msg = "知识已保存" if not error else f"知识已保存，但向量化失败：{error}"
    return ok(knowledge_dict(row), msg)


@router.put("/{knowledge_id}")
def update_knowledge(knowledge_id: int, form: KnowledgeForm, db: Session = Depends(get_db), admin: User = Depends(get_admin)):
    """更新知识并重新向量化。"""
    row = db.get(Knowledge, knowledge_id)
    if row is None:
        raise HTTPException(status_code=404, detail="知识不存在")
    row.title = form.title
    row.category = form.category
    row.content = form.content
    row.source_file = form.source_file
    row.update_time = datetime.now()
    db.commit()
    error = vectorize_row(db, row)
    db.refresh(row)
    msg = "知识已更新" if not error else f"知识已更新，但向量化失败：{error}"
    return ok(knowledge_dict(row), msg)


@router.delete("/{knowledge_id}")
def delete_knowledge(knowledge_id: int, db: Session = Depends(get_db), admin: User = Depends(get_admin)):
    """删除知识及其向量。"""
    row = db.get(Knowledge, knowledge_id)
    if row is None:
        raise HTTPException(status_code=404, detail="知识不存在")
    delete_knowledge_vectors(knowledge_id)
    db.delete(row)
    db.commit()
    return ok(msg="知识已删除")


@router.post("/upload")
def upload_document(file: UploadFile = File(...), admin: User = Depends(get_admin)):
    """上传 txt、md、pdf 或 docx，并解析正文。"""
    url = save_upload(file, "knowledge", DOC_EXTS)
    text = read_document(resolve_upload(url)).strip()
    if not text:
        raise HTTPException(status_code=400, detail="没有从文件中解析出文本")
    return ok({"source_file": url, "filename": file.filename, "content": text})


@router.post("/{knowledge_id}/vectorize")
def vectorize(knowledge_id: int, db: Session = Depends(get_db), admin: User = Depends(get_admin)):
    """对单条知识重新建立向量。"""
    row = db.get(Knowledge, knowledge_id)
    if row is None:
        raise HTTPException(status_code=404, detail="知识不存在")
    error = vectorize_row(db, row)
    db.refresh(row)
    if error:
        raise HTTPException(status_code=400, detail=f"向量化失败：{error}")
    return ok(knowledge_dict(row), "向量化完成")


@router.post("/rebuild")
def rebuild(db: Session = Depends(get_db), admin: User = Depends(get_admin)):
    """重建全部知识向量。"""
    result = rebuild_all(db)
    return ok(result, "重建完成")


@router.post("/search")
def search(form: SearchForm, admin: User = Depends(get_admin)):
    """检索测试，不生成回答。"""
    docs = search_knowledge(form.query, k=min(max(form.top_k, 1), 8))
    return ok(docs)
