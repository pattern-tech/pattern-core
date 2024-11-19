from fastapi import APIRouter
from src.auth.routers import auth_router
from src.user.routers import user_router
from src.workspace.routers import workspace_router

api_router = APIRouter()
api_router.include_router(auth_router.router, tags=["Auth"])
api_router.include_router(user_router.router, tags=["User"])
api_router.include_router(workspace_router.router, tags=["Workspace"])
