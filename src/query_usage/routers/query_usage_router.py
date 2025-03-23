from uuid import UUID
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status

from src.db.sql_alchemy import Database
from src.auth.utils.get_token import authenticate_user
from src.util.execptions import NotFoundError, RateLimitError
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

    class Config:
        from_attributes = True


class TodayQueryUsage(BaseModel):
    today_query_count: int = Field(..., example=2)
    remaining_query_allowance: int = Field(..., example=3)
    max_query_allowance_per_day: int = Field(..., example=5)
    next_reset_time: datetime = Field(..., example="2025-03-15T15:30:20+03:30")


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
    response_model=GlobalResponse[TodayQueryUsage, Dict],
    summary="Get User Daily Query Usage",
    description="Get number of used and total number of allowed query for a user",
    response_description="Number of used and total number of allowed query for a user",
    responses={
        429: {
            "model": ExceptionResponse,
            "description": "Not credit to use service"
        },
        400: {
            "model": ExceptionResponse,
            "description": "Bad request received"
        }
    },
)
def get_user_query_usages(
    provider: Optional[str] = None,
    user_id: UUID = Depends(authenticate_user),
    db: Session = Depends(get_db),
    service: QueryUsageService = Depends(get_query_usage_service),
):
    """
    Get user query usage including the remaining query count for today and the next reset time.

    - **provider**: Optional filter by provider.
    - **user_id**: The authenticated user's ID.
    - **db**: Database session.
    - **service**: QueryUsage service handling business logic.

    Returns:
        dict: A dictionary containing:
            - today_query_count: Number of queries used today
            - max_query_allowance_per_day: Total number of allowed queries per day
            - remaining_queries_today: Number of remaining queries for today
            - next_reset_time: The datetime when the query usage will reset to zero
    """
    try:
        # Get the max query allowance for this user
        max_query_allowance = service.get_user_max_query_allowance(db, user_id)

        # Get today's query count using the new repository method
        today_query_count, _, next_reset_time = service.get_user_query_count_for_today(
            db, user_id, provider)

        # Calculate remaining queries for today
        remaining_queries_today = max(
            0, max_query_allowance - today_query_count)

        data = {
            "today_query_count": today_query_count,
            "max_query_allowance_per_day": max_query_allowance,
            "remaining_queries_today": remaining_queries_today,
            "next_reset_time": next_reset_time
        }
        return global_response(data)
    except RateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
