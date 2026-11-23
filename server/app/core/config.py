"""系统配置。"""
from dotenv import load_dotenv
import os


load_dotenv(dotenv_path=".env", override=True)


# 项目根目录，即 server 目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Settings:
    """全局配置项。"""

    # 项目名称
    APP_NAME = "基于LangGraph的AI智能电商客服系统"

    MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
    MYSQL_USERNAME = os.getenv("MYSQL_USERNAME", "")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "db_ai_customer_service")

    # MySQL 8，端口 3308，密码按要求为 123456
    DATABASE_URL = f"mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4&ssl_disabled=false"
    # JWT 密钥与有效期
    JWT_SECRET = "langgraph-ai-customer-service-secret"
    JWT_EXPIRE_HOURS = 72
    # 上传文件统一放在 D 盘 uploads
    #UPLOAD_DIR = "D:/uploads"
    UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
    # 阿里云百炼兼容接口
    LLM_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    # 代码中直接读取环境变量 OPENAI_API_KEY
    LLM_API_KEY = os.getenv("DASHSCOPE_API_KEY")
    CHAT_MODEL = "qwen4-max"
    EMBED_MODEL = "text-embedding-v4"
    EMBED_DIMENSIONS = 2048
    # Chroma 持久化目录
    CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")
    CHROMA_COLLECTION = "ecommerce_knowledge"


settings = Settings()
