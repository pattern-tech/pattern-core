from fastapi import APIRouter
from src.auth.routers import auth_router
from src.user.routers import user_router
from src.task.routers import task_router
from src.project.routers import project_router
from src.workspace.routers import workspace_router
from src.agent.routers import agent_router
from src.agent.routers import tool_admin_router

api_router = APIRouter()
api_router.include_router(auth_router.router, tags=["Auth"])
api_router.include_router(user_router.router, tags=["User"])
api_router.include_router(workspace_router.router, tags=["Workspace"])
api_router.include_router(project_router.router, tags=["Project"])
api_router.include_router(task_router.router, tags=["Task"])
api_router.include_router(agent_router.router, tags=["Agent"])
# Admin
api_router.include_router(tool_admin_router.router, tags=["Admin | Tool"])
