from fastapi import APIRouter

from src.agent.services.agent_service import AgentService
from src.db.sql_alchemy import Database

router = APIRouter(prefix="/agent")
database = Database()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_agent_service() -> AgentService:
    return AgentService()
