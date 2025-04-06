from uuid import UUID
from enum import Enum
from datetime import datetime
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from fastapi.responses import StreamingResponse
from typing import List, Optional, Dict, Literal
from fastapi import APIRouter, Depends, HTTPException, status

from src.db.sql_alchemy import Database
from src.auth.utils.get_token import authenticate_user
from src.util.execptions import NotFoundError, RateLimitError
from src.project.services.project_service import ProjectService
from src.query_usage.services.query_usage_service import QueryUsageService
from src.conversation.services.conversation_service import ConversationService
from src.util.response import global_response, GlobalResponse, ExceptionResponse

router = APIRouter(prefix="/playground/conversation")
database = Database()


def get_db():
    """
    Dependency to get a SQLAlchemy database session.
    """
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_conversation_service() -> ConversationService:
    """
    Dependency to instantiate the ConversationService.
    """
    return ConversationService()


def get_query_usage_service() -> QueryUsageService:
    """
    Dependency to instantiate the QueryUsageService.
    """
    return QueryUsageService()


def get_project_service() -> ProjectService:
    """
    Dependency to instantiate the ProjectService.
    """
    return ProjectService()


class CreateConversationInput(BaseModel):
    """
    Schema for creating a conversation.
    """
    name: str
    project_id: UUID
    conversation_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class ConversationOutput(BaseModel):
    """
    Schema for conversation output.
    """
    id: UUID
    name: str
    project_id: UUID
    created_at: datetime = Field(None, example="2025-03-15T15:30:20+03:30")
    updated_at: datetime = Field(None, example="2025-03-15T15:30:20+03:30")
    deleted_at: datetime = Field(None, example="2025-03-15T15:30:20+03:30")

    class Config:
        from_attributes = True


class MessageType(str, Enum):
    """
    Enum representing the type of a message.
    """
    TEXT = "text"
    AUDIO = "audio"


class MessageInput(BaseModel):
    """
    Schema for sending a message.
    """
    message: str
    message_type: MessageType = MessageType.TEXT
    stream: bool = True


class FirstMessage(BaseModel):
    """
    Schema for the first message.
    """
    message: str


class HistoryMessage(BaseModel):
    """
    Schema for the history message.
    """
    id: int
    role: Literal["ai", "human"]
    content: str


class ChatHistory(BaseModel):
    """
    Schema for chat history.
    """
    history: List[HistoryMessage]


class TitleOutput(BaseModel):
    """
    Schema for title output.
    """
    title: str


@router.post(
    "",
    response_model=GlobalResponse[ConversationOutput, Dict],
    summary="Create Conversation",
    description="Creates a new conversation for the authenticated user.",
    response_description="The created conversation data.",
    responses={
        400: {
            "model": ExceptionResponse,
            "description": "Bad request received."
        },
        404: {
            "model": ExceptionResponse,
            "description": "Project not found"
        }
    },
)
def create_conversation(
    input: CreateConversationInput,
    db: Session = Depends(get_db),
    service: ConversationService = Depends(get_conversation_service),
    user_id: UUID = Depends(authenticate_user)
):
    """
    Create a new conversation.

    - **input**: The conversation creation input containing the conversation name and project ID.
    - **db**: Database session.
    - **service**: Conversation service handling business logic.
    - **user_id**: The authenticated user's ID.

    Returns:
        ConversationOutput: The created conversation data.
    """
    try:
        conversation = service.create_conversation(
            db, input.name, input.project_id, user_id, input.conversation_id)
        return global_response(conversation)

    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/{project_id}/{conversation_id}",
    response_model=GlobalResponse[ConversationOutput, ChatHistory],
    summary="Get Conversation",
    description="Retrieves a conversation by its ID for the authenticated user along with chat history metadata.",
    response_description="The conversation data with chat history metadata.",
    responses={
        404: {
            "model": ExceptionResponse,
            "description": "Conversation not found"
        },
        400: {
            "model": ExceptionResponse,
            "description": "Bad request received"
        }
    },
)
def get_conversation(
    project_id: UUID,
    conversation_id: UUID,
    db: Session = Depends(get_db),
    service: ConversationService = Depends(get_conversation_service),
    user_id: UUID = Depends(authenticate_user),
):
    """
    Retrieve a conversation by its ID.

    - **project_id**: The project ID associated with the conversation.
    - **conversation_id**: The ID of the conversation to retrieve.
    - **db**: Database session.
    - **service**: Conversation service handling business logic.
    - **user_id**: The authenticated user's ID.

    - **metadata**: The chat history metadata.

    Returns:
        ConversationOutput: The conversation data with chat history metadata.
    """
    try:

        conversation, history = service.get_conversation(
            db, conversation_id, user_id)
        return global_response(content=conversation, metadata={"history": history})

    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.get(
    "/{project_id}",
    response_model=GlobalResponse[List[ConversationOutput], Dict],
    summary="List All Conversations",
    description="Lists all conversations for a specific project for the authenticated user.",
    response_description="A list of all conversations for the project.",
    responses={
        404: {
            "model": ExceptionResponse,
            "description": "Project not found"
        },
        400: {
            "model": ExceptionResponse,
            "description": "Bad request received"
        }
    },
)
def get_all_conversations(
    project_id: UUID,
    db: Session = Depends(get_db),
    service: ConversationService = Depends(get_conversation_service),
    user_id: UUID = Depends(authenticate_user),
):
    """
    List all conversations for a specific project.

    - **project_id**: The ID of the project for which to list conversations.
    - **db**: Database session.
    - **service**: Conversation service handling business logic.
    - **user_id**: The authenticated user's ID.

    Returns:
        List[ConversationOutput]: A list of all conversations for the project.
    """
    try:
        conversations = service.get_all_conversations(db, project_id, user_id)
        return global_response(conversations)

    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put(
    "/{project_id}/{conversation_id}",
    response_model=ConversationOutput,
    summary="Update Conversation",
    description="Updates an existing conversation by its ID for the authenticated user.",
    response_description="The updated conversation data."
)
def update_conversation(
    project_id: UUID,
    conversation_id: UUID,
    input: CreateConversationInput,
    db: Session = Depends(get_db),
    service: ConversationService = Depends(get_conversation_service),
    user_id: UUID = Depends(authenticate_user),
):
    """
    Update an existing conversation.

    - **project_id**: The project ID associated with the conversation.
    - **conversation_id**: The ID of the conversation to update.
    - **input**: The conversation update input containing the new conversation name and project ID.
    - **db**: Database session.
    - **service**: Conversation service handling business logic.
    - **user_id**: The authenticated user's ID.

    Returns:
        ConversationOutput: The updated conversation data.
    """
    try:
        # TODO: fix update conversation if necessary
        updated_conversation = service.update_conversation(
            db, conversation_id, input.dict(), user_id)
        return global_response(updated_conversation)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.delete(
    "/{project_id}/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Conversation",
    description="Deletes a conversation by its ID for the authenticated user.",
    response_description="No content if the conversation is successfully deleted.",
    responses={
        404: {
            "model": ExceptionResponse,
            "description": "Project not found"
        },
        400: {
            "model": ExceptionResponse,
            "description": "Bad request received"
        }
    }
)
def delete_conversation(
    project_id: UUID,
    conversation_id: UUID,
    db: Session = Depends(get_db),
    service: ConversationService = Depends(get_conversation_service),
    user_id: UUID = Depends(authenticate_user),
):
    """
    Delete a conversation by its ID.

    - **project_id**: The project ID associated with the conversation.
    - **conversation_id**: The ID of the conversation to delete.
    - **db**: Database session.
    - **service**: Conversation service handling business logic.
    - **user_id**: The authenticated user's ID.

    Returns:
        None: If the conversation is successfully deleted.
    """
    try:
        conversation = service.delete_conversation(
            db, conversation_id, user_id)
        return global_response(conversation)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.post(
    "/{project_id}/{conversation_id}/chat",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Send Message",
    description="Sends a message in the conversation chat for the authenticated user.",
    response_description="The message response data along with chat history in metadata.",
    responses={
        404: {
            "model": ExceptionResponse,
            "description": "Conversation or Project not found"
        },
        400: {
            "model": ExceptionResponse,
            "description": "Bad request received"
        },
        429: {
            "model": ExceptionResponse,
            "description": "Rate daily limit exceeded"
        }
    }
)
def send_message(
    input: MessageInput,
    conversation_id: UUID,
    project_id: UUID,
    db: Session = Depends(get_db),
    query_usage_service: QueryUsageService = Depends(get_query_usage_service),
    conversation_service: ConversationService = Depends(
        get_conversation_service),
    user_id: UUID = Depends(authenticate_user),
):
    """
    Send a message in a conversation chat.

    - **input**: The message input containing the message content, message type and streaming.
    - **conversation_id**: The ID of the conversation.
    - **project_id**: The project ID associated with the conversation.
    - **db**: Database session.
    - **service**: Conversation service handling business logic.
    - **user_id**: The authenticated user's ID.

    Returns:
        StreamingResponse: If `stream` is true.
        dict: A JSON response containing the complete message data if `stream` is false.

        metadata: The chat history metadata.
    """
    try:
        max_query_allowance = query_usage_service.get_user_max_query_allowance(
            db, user_id)

        is_eligible = query_usage_service.check_user_eligibility(
            db, user_id, max_query_allowance)
        if not is_eligible:
            raise RateLimitError(
                "You have reached your daily query limit. Please try again tomorrow or stake more to get more credit.")
        result = conversation_service.send_message(db,
                                                   input.message,
                                                   user_id,
                                                   conversation_id,
                                                   project_id,
                                                   input.message_type,
                                                   input.stream)

        return global_response(result)

    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
    except RateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/{project_id}/{conversation_id}/title-generation",
    response_model=GlobalResponse[TitleOutput, Dict],
    summary="Auto Title Generation",
    description="Using LLM to generate title for conversation",
    response_description="LLM title generated",
    responses={
            400: {
                "model": ExceptionResponse,
                "description": "Bad request received"
            }
    },
)
async def generate_title(
    input: FirstMessage,
    project_id: UUID,
    conversation_id: UUID,
    db: Session = Depends(get_db),
    conversation_service: ConversationService = Depends(
        get_conversation_service),
    user_id: UUID = Depends(authenticate_user),
):
    try:
        title = conversation_service.rename_title(
            db, conversation_id, user_id, input.message)
        return global_response({"title": title})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
