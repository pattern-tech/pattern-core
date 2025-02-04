from fastapi.responses import StreamingResponse
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


class CreateConversationInput(BaseModel):
    """
    Schema for creating a conversation.
    """
    name: str
    project_id: UUID

    class Config:
        orm_mode = True


class ConversationOutput(BaseModel):
    """
    Schema for conversation output.
    """
    id: UUID
    name: str
    project_id: UUID

    class Config:
        orm_mode = True


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


@router.post(
    "",
    response_model=ConversationOutput,
    summary="Create Conversation",
    description="Creates a new conversation for the authenticated user.",
    response_description="The created conversation data."
)
def create_conversation(
    input: CreateConversationInput,
    db: Session = Depends(get_db),
    service: ConversationService = Depends(get_conversation_service),
    user_id: UUID = Depends(authenticate_user),
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
            db, input.name, input.project_id, user_id)
        return global_response(conversation)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.get(
    "/{project_id}/{conversation_id}",
    response_model=ConversationOutput,
    summary="Get Conversation",
    description="Retrieves a conversation by its ID for the authenticated user along with chat history metadata.",
    response_description="The conversation data with chat history metadata."
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

    Returns:
        ConversationOutput: The conversation data with chat history metadata.
    """
    try:
        conversation, history = service.get_conversation(
            db, conversation_id, user_id)
        return global_response(content=conversation, metadata={"history": history})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@router.get(
    "/{project_id}",
    response_model=List[ConversationOutput],
    summary="List All Conversations",
    description="Lists all conversations for a specific project for the authenticated user.",
    response_description="A list of all conversations for the project."
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
    conversations = service.get_all_conversations(db, project_id)
    return global_response(conversations)


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
    summary="Delete Conversation",
    description="Deletes a conversation by its ID for the authenticated user.",
    response_description="No content if the conversation is successfully deleted."
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
        service.delete_conversation(db, conversation_id, user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.post(
    "/{project_id}/{conversation_id}/chat",
    summary="Send Message",
    description="Sends a message in the conversation chat for the authenticated user.",
    response_description="The message response data along with intermediate steps metadata."
)
async def send_message(
    input: MessageInput,
    conversation_id: UUID,
    project_id: UUID,
    db: Session = Depends(get_db),
    service: ConversationService = Depends(get_conversation_service),
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
    """
    try:

        if input.stream:
            return StreamingResponse(
                service.send_message(db, input.message, user_id,
                                     conversation_id, input.message_type, input.stream),
                media_type="text/plain"
            )
        else:
            response = None
            async for item in service.send_message(
                db,
                input.message,
                user_id,
                conversation_id,
                input.message_type,
                input.stream
            ):
                response = item
            metadata = {"intermediate_steps": response["intermediate_steps"]}
            return global_response(content=response["response"], metadata=metadata)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
