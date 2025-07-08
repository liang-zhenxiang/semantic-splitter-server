from typing import Any, Dict, Union

from fastapi import APIRouter

from .splitter import router as base_router


v1_router = APIRouter(prefix="/service")


v1_router.include_router(base_router)
