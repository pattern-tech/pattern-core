from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status

from src.db.sql_alchemy import Database
from src.auth.utils.get_token import authenticate_user
from src.util.execptions import NotFoundError, NotEnoughBalanceError
from src.query_usage.services.query_usage_service import QueryUsageService
from src.util.response import global_response, GlobalResponse, ExceptionResponse

router = APIRouter(prefix="/query-usage")
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


def get_query_usage_service() -> QueryUsageService:
    """
    Dependency to instantiate the QueryUsageService.
    """
    return QueryUsageService()


class CreateQueryUsageInput(BaseModel):
    """
    Schema for creating a query usage record.
    """
    provider: str = Field(..., example="morpheus")

    class Config:
        from_attributes = True


class QueryUsageOutput(BaseModel):
    """
    Schema for query usage output.
    """
    id: UUID = Field(..., example="123e4567-e89b-12d3-a456-426614174000")
    provider: str = Field(..., example="morpheus")
    created_at: datetime = Field(None, example="2025-03-15T15:30:20+03:30")
    updated_at: datetime = Field(None, example="2025-03-15T15:30:20+03:30")
    deleted_at: datetime = Field(None, example="2025-03-15T15:30:20+03:30")

    class Config:
        from_attributes = True


@router.get(
    "/{query_usage_id}",
    response_model=GlobalResponse[QueryUsageOutput, Dict],
    summary="Get Query Usage",
    description="Retrieves a query usage record by its ID for the authenticated user.",
    response_description="The query usage data.",
    responses={
        404: {
            "model": ExceptionResponse,
            "description": "Query Usage not found"
        },
        400: {
            "model": ExceptionResponse,
            "description": "Bad request received"
        }
    },
)
def get_query_usage(
    query_usage_id: UUID,
    user_id: UUID = Depends(authenticate_user),
    db: Session = Depends(get_db),
    service: QueryUsageService = Depends(get_query_usage_service),
):
    """
    Retrieve a query usage record by its ID.

    - **query_usage_id**: The ID of the query usage record to retrieve.
    - **user_id**: The authenticated user's ID.
    - **db**: Database session.
    - **service**: QueryUsage service handling business logic.

    Returns:
        QueryUsageOutput: The query usage details if found.
    """
    try:
        query_usage = service.get_query_usage(db, query_usage_id)
        return global_response(query_usage)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "",
    response_model=GlobalResponse[List[QueryUsageOutput], Dict],
    summary="Get user query usage",
    description="Get number of used and total number of allowed query for a user",
    response_description="Number of used and total number of allowed query for a user",
    responses={
        429: {
            "model": ExceptionResponse,
            "description": "Not enough balance"
        },
        400: {
            "model": ExceptionResponse,
            "description": "Bad request received"
        }
    },
)
def get_user_query_usages(
    provider: Optional[str] = None,
    duration: Optional[timedelta] = timedelta(hours=24),
    user_id: UUID = Depends(authenticate_user),
    db: Session = Depends(get_db),
    service: QueryUsageService = Depends(get_query_usage_service),
):
    """
    Get user query usage

    - **provider**: Optional filter by provider.
    - **duration**: Optional filter by a specific datetime.
    - **user_id**: The authenticated user's ID.
    - **db**: Database session.
    - **service**: QueryUsage service handling business logic.
    - **conversation_service**: Conversation service handling business logic.

    Returns:
        dict: A dictionary containing the number of used and total number of allowed query.
    """
    try:
        query_usages = service.get_all_query_usages(
            db, user_id, provider, duration)

        data = {
            "query_usages": len(query_usages),
            "max_query_allowance_per_day": service.get_user_max_query_allowance(db, user_id)
        }
        return global_response(data)
    except NotEnoughBalanceError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
