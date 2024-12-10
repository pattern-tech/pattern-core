from enum import Enum
from uuid import UUID
from typing import List
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status

from src.db.sql_alchemy import Database
from src.util.response import global_response
from src.auth.utils.get_token import authenticate_user
from src.playground.services.playground_service import PlayGroundService

router = APIRouter(prefix="/playground")
database = Database()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_playground_service() -> PlayGroundService:
    return PlayGroundService()


class MessageType(str, Enum):
    TEXT = "text"
    AUDIO = "audio"


class MessageInput(BaseModel):
    message: str
    conversation_id: UUID
    project_id: UUID
    message_type: MessageType = MessageType.TEXT


@router.post("/chat")
def send_message(
    input: MessageInput,
    db: Session = Depends(get_db),
    service: PlayGroundService = Depends(get_playground_service),
    user_id: UUID = Depends(authenticate_user),
):
    """
    Sends a message in the playground.

    Args:
        input (MessageInput): The message input.

    Returns:
        MessageOutput: The message data.
    """
    try:
        response = service.send_message(
            db,
            input.message,
            user_id,
            input.conversation_id,
            input.project_id,
            input.message_type,
        )
        metadata = {"intermediate_steps": response["intermediate_steps"]}
        return global_response(content=response["response"], metadata=metadata)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.get("/chat/{conversation_id}")
def get_hisotry(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    service: PlayGroundService = Depends(get_playground_service),
    user_id: UUID = Depends(authenticate_user),
):
    """
    Retrieves messages history for a specific conversation.

    Args:
        conversation_id (UUID): The ID of the conversation to retrieve messages for.

    Returns:
        List[MessageOutput]: List of messages for the conversation.
    """
    try:
        messages = service.get_hisotry(db, user_id, conversation_id)
        return global_response(messages)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
