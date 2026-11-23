"""商品管理。"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import ok, page_data, paginate
from app.core.security import get_admin
from app.models.entities import Product, User
from app.schemas.schemas import ProductForm, product_dict

router = APIRouter(prefix="/products", tags=["商品"])


@router.get("")
def list_products(
    page: int = 1,
    page_size: int = 10,
    keyword: str = "",
    category: str = "",
    status: str = "",
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin),
):
    """分页查询商品。"""
    query = db.query(Product)
    if keyword:
        query = query.filter(Product.name.like(f"%{keyword}%"))
    if category:
        query = query.filter(Product.category == category)
    if status in ("0", "1"):
        query = query.filter(Product.status == int(status))
    query = query.order_by(Product.id.desc())
    total, rows = paginate(query, page, page_size)
    return ok(page_data([product_dict(row) for row in rows], total))


@router.post("")
def create_product(form: ProductForm, db: Session = Depends(get_db), admin: User = Depends(get_admin)):
    """新增商品。"""
    now = datetime.now()
    row = Product(**form.model_dump(), create_time=now, update_time=now)
    db.add(row)
    db.commit()
    db.refresh(row)
    return ok(product_dict(row), "商品已新增")


@router.put("/{product_id}")
def update_product(product_id: int, form: ProductForm, db: Session = Depends(get_db), admin: User = Depends(get_admin)):
    """编辑商品。"""
    row = db.get(Product, product_id)
    if row is None:
        raise HTTPException(status_code=404, detail="商品不存在")
    for key, value in form.model_dump().items():
        setattr(row, key, value)
    row.update_time = datetime.now()
    db.commit()
    db.refresh(row)
    return ok(product_dict(row), "商品已更新")


@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), admin: User = Depends(get_admin)):
    """删除商品。"""
    row = db.get(Product, product_id)
    if row is None:
        raise HTTPException(status_code=404, detail="商品不存在")
    db.delete(row)
    db.commit()
    return ok(msg="商品已删除")
