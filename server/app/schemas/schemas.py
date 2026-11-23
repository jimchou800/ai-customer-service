"""接口入参与出参模型。"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def format_time(value):
    """把时间格式化成 2026-11-02 17:25:17。"""
    if value is None or value == "":
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    return str(value)


class OrmModel(BaseModel):
    """支持从 SQLAlchemy 对象转换。"""

    model_config = ConfigDict(from_attributes=True)


class LoginForm(BaseModel):
    """登录表单。"""

    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=50)


class RegisterForm(BaseModel):
    """注册表单，包含确认密码。"""

    username: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=6, max_length=20)
    confirm_password: str = Field(min_length=6, max_length=20)
    nickname: str = Field(min_length=1, max_length=50)
    gender: str = "男"
    phone: str = ""
    email: str = ""

    @field_validator("gender")
    @classmethod
    def check_gender(cls, value: str) -> str:
        """性别只允许男或女，默认男。"""
        if value not in ("男", "女"):
            raise ValueError("性别只能是男或女")
        return value

    @model_validator(mode="after")
    def check_password(self):
        """校验两次密码一致。"""
        if self.password != self.confirm_password:
            raise ValueError("两次输入的密码不一致")
        return self


class ProfileForm(BaseModel):
    """个人资料修改。"""

    nickname: str = Field(min_length=1, max_length=50)
    gender: str = "男"
    phone: str = ""
    email: str = ""

    @field_validator("gender")
    @classmethod
    def check_gender(cls, value: str) -> str:
        """性别只允许男或女。"""
        if value not in ("男", "女"):
            raise ValueError("性别只能是男或女")
        return value


class PasswordForm(BaseModel):
    """修改密码。"""

    old_password: str
    new_password: str = Field(min_length=6, max_length=20)
    confirm_password: str

    @model_validator(mode="after")
    def check_password(self):
        """校验两次新密码一致。"""
        if self.new_password != self.confirm_password:
            raise ValueError("两次输入的密码不一致")
        return self


class UserSaveForm(BaseModel):
    """管理员维护用户。"""

    username: str = Field(min_length=3, max_length=20)
    nickname: str = Field(min_length=1, max_length=50)
    password: str = ""
    confirm_password: str = ""
    gender: str = "男"
    phone: str = ""
    email: str = ""
    role: str = "user"
    status: int = 1

    @field_validator("gender")
    @classmethod
    def check_gender(cls, value: str) -> str:
        """性别只允许男或女。"""
        if value not in ("男", "女"):
            raise ValueError("性别只能是男或女")
        return value

    @model_validator(mode="after")
    def check_password(self):
        """填写密码时必须与确认密码一致。"""
        if self.password or self.confirm_password:
            if self.password != self.confirm_password:
                raise ValueError("两次输入的密码不一致")
        return self


class ProductForm(BaseModel):
    """商品新增与编辑。"""

    name: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=50)
    price: float = Field(ge=0)
    stock: int = Field(ge=0)
    image: str = ""
    description: str = ""
    status: int = 1


class ShipForm(BaseModel):
    """订单发货。"""

    logistics_company: str = Field(min_length=1, max_length=50)
    logistics_no: str = Field(min_length=1, max_length=50)


class OrderStatusForm(BaseModel):
    """修改订单状态。"""

    status: str


class KnowledgeForm(BaseModel):
    """知识库文档。"""

    title: str = Field(min_length=1, max_length=120)
    category: str = Field(min_length=1, max_length=50)
    content: str = Field(min_length=1)
    source_file: str = ""


class SearchForm(BaseModel):
    """知识库检索测试。"""

    query: str = Field(min_length=1)
    top_k: int = 4


class TicketHandleForm(BaseModel):
    """工单处理。"""

    status: str
    reply: str = ""


class ChatSendForm(BaseModel):
    """发送客服消息，可附带图片。"""

    content: str = ""
    image_urls: list[str] = []


class UserOut(OrmModel):
    """返回给前端的用户信息，不包含密码。"""

    id: int
    username: str
    nickname: str
    avatar: str = ""
    gender: str = "男"
    phone: str = ""
    email: str = ""
    role: str
    status: int
    create_time: Optional[datetime] = None

    @field_validator("create_time", mode="before")
    @classmethod
    def empty_time(cls, value):
        """允许空时间。"""
        return value or None


def user_dict(user) -> dict:
    """用户对象转字典，并格式化时间。"""
    data = UserOut.model_validate(user).model_dump()
    data["avatar"] = data.get("avatar") or ""
    data["phone"] = data.get("phone") or ""
    data["email"] = data.get("email") or ""
    data["create_time"] = format_time(user.create_time)
    return data


def product_dict(row) -> dict:
    """商品对象转字典。"""
    return {
        "id": row.id,
        "name": row.name,
        "category": row.category,
        "price": float(row.price or 0),
        "stock": row.stock,
        "image": row.image or "",
        "description": row.description or "",
        "status": row.status,
        "create_time": format_time(row.create_time),
        "update_time": format_time(row.update_time),
    }


def order_dict(row, nickname="", items=None) -> dict:
    """订单对象转字典。"""
    return {
        "id": row.id,
        "order_no": row.order_no,
        "user_id": row.user_id,
        "nickname": nickname,
        "total_amount": float(row.total_amount or 0),
        "status": row.status,
        "receiver": row.receiver,
        "phone": row.phone,
        "address": row.address,
        "logistics_company": row.logistics_company or "",
        "logistics_no": row.logistics_no or "",
        "pay_method": row.pay_method or "",
        "create_time": format_time(row.create_time),
        "pay_time": format_time(row.pay_time),
        "ship_time": format_time(row.ship_time),
        "finish_time": format_time(row.finish_time),
        "items": items or [],
    }


def item_dict(row) -> dict:
    """订单明细转字典。"""
    return {
        "id": row.id,
        "product_id": row.product_id,
        "product_name": row.product_name,
        "price": float(row.price or 0),
        "quantity": row.quantity,
        "image": row.image or "",
    }
