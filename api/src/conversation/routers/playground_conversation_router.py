from uuid import UUID
from enum import Enum
from typing import List
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status

from src.db.sql_alchemy import Database
from src.util.response import global_response
from src.auth.utils.get_token import authenticate_user
from src.conversation.services.conversation_service import ConversationService

router = APIRouter(prefix="/playground/conversation")
database = Database()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_conversation_service() -> ConversationService:
    return ConversationService()


class CreateConversationInput(BaseModel):
    name: str
    project_id: UUID

    class Config:
        orm_mode = True


class ConversationOutput(BaseModel):
    id: UUID
    name: str
    project_id: UUID

    class Config:
        orm_mode = True


class MessageType(str, Enum):
    TEXT = "text"
    AUDIO = "audio"


class MessageInput(BaseModel):
    message: str
    message_type: MessageType = MessageType.TEXT


@router.post("", response_model=ConversationOutput)
def create_conversation(
    input: CreateConversationInput,
    db: Session = Depends(get_db),
    service: ConversationService = Depends(get_conversation_service),
    user_id: UUID = Depends(authenticate_user),
):
    """
    Creates a new conversation.

    Args:
        input (CreateConversationInput): The conversation creation input.

    Returns:
        ConversationOutput: The created conversation data.
    """
    try:
        conversation = service.create_conversation(
            db, input.name, input.project_id, user_id)
        return global_response(conversation)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.get("/{conversation_id}", response_model=ConversationOutput)
def get_conversation(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    service: ConversationService = Depends(get_conversation_service),
    user_id: UUID = Depends(authenticate_user),
):
    """
    Retrieves a conversation by its ID.

    Args:
        conversation_id (UUID): The conversation ID.

    Returns:
        ConversationOutput: The conversation data and chat history metadata.

    Raises:
        HTTPException: If conversation is not found or user is not authorized.
    """
    try:
        conversation, history = service.get_conversation(
            db, conversation_id, user_id)
        return global_response(content=conversation, metadata={"history": history})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@router.get("", response_model=List[ConversationOutput])
def get_all_conversations(
    project_id: UUID,
    db: Session = Depends(get_db),
    service: ConversationService = Depends(get_conversation_service),
    user_id: UUID = Depends(authenticate_user),
):
    """
    Lists all conversations for a specific project.

    Args:
        project_id (UUID): The ID of the project to retrieve conversations for.

    Returns:
        List[ConversationOutput]: List of all conversations for the project.
    """
    conversations = service.get_all_conversations(db, project_id)
    return global_response(conversations)


@router.put("/{conversation_id}", response_model=ConversationOutput)
def update_conversation(
    conversation_id: UUID,
    input: CreateConversationInput,
    db: Session = Depends(get_db),
    service: ConversationService = Depends(get_conversation_service),
    user_id: UUID = Depends(authenticate_user),
):
    """
    Updates an existing conversation by its ID.

    Args:
        conversation_id (UUID): The conversation ID.

    Returns:
        ConversationOutput: The updated conversation data.
    """
    try:
        updated_conversation = service.update_conversation(
            db, conversation_id, input.dict(), input.project_id
        )
        return global_response(updated_conversation)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: UUID,
    project_id: UUID,
    db: Session = Depends(get_db),
    service: ConversationService = Depends(get_conversation_service),
    user_id: UUID = Depends(authenticate_user),
):
    """
    Deletes a conversation by its ID.

    Args:
        conversation_id (UUID): The conversation ID.

    Returns:
        None
    """
    try:
        service.delete_conversation(db, conversation_id, project_id)
        return global_response({"detail": "Conversation deleted successfully."})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.post("/{conversation_id}/chat")
def send_message(
    input: MessageInput,
    conversation_id: UUID,
    db: Session = Depends(get_db),
    service: ConversationService = Depends(get_conversation_service),
    user_id: UUID = Depends(authenticate_user),
):
    """
    Sends a message in the chat.

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
            conversation_id,
            input.message_type,
        )
        metadata = {"intermediate_steps": response["intermediate_steps"]}
        return global_response(content=response["response"], metadata=metadata)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
