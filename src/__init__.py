from fastapi import APIRouter

from src.auth.routers import auth_router
from src.user.routers import user_router
from src.project.routers import project_router
from src.workspace.routers import workspace_router
from src.query_usage.routers import query_usage_router
from src.conversation.routers import playground_conversation_router

api_router = APIRouter()
api_router.include_router(auth_router.router, tags=["Auth"])
api_router.include_router(user_router.router, tags=["User"])
api_router.include_router(workspace_router.router, tags=["Workspace"])
api_router.include_router(project_router.router, tags=["Project"])
api_router.include_router(
    playground_conversation_router.router, tags=["Conversation"])
api_router.include_router(query_usage_router.router, tags=["Query Usage"])
