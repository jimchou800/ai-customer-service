"""数据库实体，表名均以 t_ 开头。"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    """用户，包含管理员和普通用户。"""

    __tablename__ = "t_user"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    username = Column(String(50), unique=True, nullable=False, comment="用户名")
    password = Column(String(50), nullable=False, comment="明文密码")
    nickname = Column(String(50), nullable=False, comment="昵称")
    avatar = Column(String(255), default="", comment="头像")
    gender = Column(String(10), nullable=False, default="男", comment="性别")
    phone = Column(String(20), default="", comment="手机号")
    email = Column(String(100), default="", comment="邮箱")
    role = Column(String(20), nullable=False, default="user", comment="角色")
    status = Column(Integer, nullable=False, default=1, comment="状态")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, comment="更新时间")


class Product(Base):
    """电商商品。"""

    __tablename__ = "t_product"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    name = Column(String(100), nullable=False, comment="名称")
    category = Column(String(50), nullable=False, comment="分类")
    price = Column(Numeric(10, 2), nullable=False, comment="单价")
    stock = Column(Integer, nullable=False, default=0, comment="库存")
    image = Column(String(255), default="", comment="图片")
    description = Column(String(500), default="", comment="描述")
    status = Column(Integer, nullable=False, default=1, comment="上下架")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, comment="更新时间")


class Order(Base):
    """用户订单。"""

    __tablename__ = "t_order"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    order_no = Column(String(40), unique=True, nullable=False, comment="订单号")
    user_id = Column(Integer, nullable=False, comment="用户编号")
    total_amount = Column(Numeric(10, 2), nullable=False, comment="金额")
    status = Column(String(20), nullable=False, comment="状态")
    receiver = Column(String(50), nullable=False, comment="收货人")
    phone = Column(String(20), nullable=False, comment="电话")
    address = Column(String(255), nullable=False, comment="地址")
    logistics_company = Column(String(50), default="", comment="物流公司")
    logistics_no = Column(String(50), default="", comment="物流单号")
    pay_method = Column(String(20), default="", comment="支付方式")
    create_time = Column(DateTime, default=datetime.now, comment="下单时间")
    pay_time = Column(DateTime, comment="支付时间")
    ship_time = Column(DateTime, comment="发货时间")
    finish_time = Column(DateTime, comment="完成时间")


class OrderItem(Base):
    """订单商品明细。"""

    __tablename__ = "t_order_item"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    order_id = Column(Integer, nullable=False, comment="订单编号")
    product_id = Column(Integer, nullable=False, comment="商品编号")
    product_name = Column(String(100), nullable=False, comment="商品名称")
    price = Column(Numeric(10, 2), nullable=False, comment="单价")
    quantity = Column(Integer, nullable=False, comment="数量")
    image = Column(String(255), default="", comment="图片")


class Knowledge(Base):
    """电商知识库文档。"""

    __tablename__ = "t_knowledge"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    title = Column(String(120), nullable=False, comment="标题")
    category = Column(String(50), nullable=False, comment="分类")
    content = Column(Text, nullable=False, comment="正文")
    source_file = Column(String(255), default="", comment="来源文件")
    vector_status = Column(String(20), default="未向量化", comment="向量状态")
    chunk_count = Column(Integer, default=0, comment="切片数量")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, comment="更新时间")


class Ticket(Base):
    """客服升级工单。"""

    __tablename__ = "t_ticket"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    ticket_no = Column(String(40), unique=True, nullable=False, comment="工单号")
    user_id = Column(Integer, nullable=False, comment="用户编号")
    session_id = Column(Integer, comment="会话编号")
    title = Column(String(120), nullable=False, comment="标题")
    content = Column(Text, nullable=False, comment="问题描述")
    category = Column(String(50), nullable=False, comment="分类")
    priority = Column(String(10), nullable=False, comment="优先级")
    status = Column(String(20), nullable=False, comment="状态")
    reply = Column(Text, default="", comment="处理回复")
    handler_id = Column(Integer, comment="处理人")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, comment="更新时间")


class ChatSession(Base):
    """智能客服会话。"""

    __tablename__ = "t_chat_session"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    user_id = Column(Integer, nullable=False, comment="用户编号")
    title = Column(String(100), nullable=False, comment="标题")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, comment="更新时间")


class ChatMessage(Base):
    """智能客服消息。"""

    __tablename__ = "t_chat_message"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    session_id = Column(Integer, nullable=False, comment="会话编号")
    role = Column(String(20), nullable=False, comment="角色")
    content = Column(Text, default="", comment="内容")
    images = Column(Text, default="", comment="图片JSON")
    intent = Column(String(30), default="", comment="意图")
    agent_name = Column(String(30), default="", comment="智能体")
    sources = Column(Text, default="", comment="来源JSON")
    create_time = Column(DateTime, default=datetime.now, comment="发送时间")
