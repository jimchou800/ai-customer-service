"""数据库连接。"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# pool_pre_ping 避免 MySQL 连接空闲断开
print(settings.DATABASE_URL)
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    """提供请求级别的数据库会话。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
