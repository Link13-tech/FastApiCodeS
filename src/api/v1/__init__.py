from fastapi import APIRouter

from .auth import auth_router
from .user import user_router
from .snippet import snippet_router


api_router = APIRouter()

api_router.include_router(user_router)
api_router.include_router(snippet_router)
api_router.include_router(auth_router)
