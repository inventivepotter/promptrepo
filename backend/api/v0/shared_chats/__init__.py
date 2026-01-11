"""
Shared chats API module.
"""
from fastapi import APIRouter

from .create import router as create_router
from .get import router as get_router
from .list_delete import router as list_delete_router

router = APIRouter()

router.include_router(create_router)
router.include_router(get_router)
router.include_router(list_delete_router)
