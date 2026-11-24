"""基于LangGraph的AI智能电商客服系统入口。"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.files import ensure_upload_dirs
from app.routers import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时准备上传目录，并在向量库为空时同步知识库。"""
    ensure_upload_dirs()
    db = SessionLocal()
    try:
        from app.rag.vector_store import sync_if_empty

        sync_if_empty(db)
    except Exception as exc:
        print(f"知识库向量同步跳过：{exc}")
    finally:
        db.close()
    yield


ensure_upload_dirs()
app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


@app.exception_handler(HTTPException)
async def handle_http_error(request, exc: HTTPException):
    """把业务异常转成统一结构。"""
    message = exc.detail if isinstance(exc.detail, str) else "请求失败"
    return JSONResponse({"code": exc.status_code, "msg": message, "data": None}, status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def handle_validation_error(request, exc: RequestValidationError):
    """提取第一条参数错误。"""
    message = "参数错误"
    if exc.errors():
        raw = exc.errors()[0].get("msg") or message
        message = raw.replace("Value error, ", "")
    return JSONResponse({"code": 422, "msg": message, "data": None}, status_code=422)


@app.get("/api/health")
def health():
    """健康检查。"""
    return {"code": 200, "msg": "成功", "data": {"name": settings.APP_NAME}}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
