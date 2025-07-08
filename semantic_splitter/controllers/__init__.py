"""
Semantic Splitter Server 控制器模块
"""

from fastapi import APIRouter

from .service_api.v1 import v1_router as console_v1_router


# 创建主路由
api_router = APIRouter()

# 注册路由
api_router.include_router(console_v1_router, prefix="/v1")

# 导入所有控制器
# from .text_splitter import router as text_splitter_router

# 注册路由
# api_router.include_router(text_splitter_router, prefix="/text-splitter", tags=["文本分割"])

__all__ = ["api_router"]
