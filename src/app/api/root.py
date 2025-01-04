from fastapi import APIRouter

from .index import index_router
from .stocks import stock_router

root_router = APIRouter()
root_router.include_router(
    stock_router,
    prefix="/stock",
)
root_router.include_router(
    index_router,
)
