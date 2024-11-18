from fastapi import APIRouter
from src.auth.routers import auth_router
from src.user.routers import user_router

api_router = APIRouter()
api_router.include_router(auth_router.router, tags=["Auth"])
api_router.include_router(user_router.router, tags=["User"])
