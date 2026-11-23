"""汇总全部业务路由。"""
from fastapi import APIRouter

from app.routers import auth, chat, dashboard, knowledge, order, product, profile, ticket, upload, user

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(profile.router)
api_router.include_router(dashboard.router)
api_router.include_router(product.router)
api_router.include_router(order.router)
api_router.include_router(knowledge.router)
api_router.include_router(ticket.router)
api_router.include_router(user.router)
api_router.include_router(upload.router)
api_router.include_router(chat.router)
