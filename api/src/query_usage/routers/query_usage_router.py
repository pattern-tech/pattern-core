from uuid import UUID
from typing import List, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status

from src.db.sql_alchemy import Database
from src.util.response import global_response
from src.auth.utils.get_token import authenticate_user
from src.query_usage.services.query_usage_service import QueryUsageService


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
        orm_mode = True


class QueryUsageOutput(BaseModel):
    """
    Schema for query usage output.
    """
    id: UUID = Field(..., example="123e4567-e89b-12d3-a456-426614174000")
    provider: str = Field(..., example="morpheus")

    class Config:
        orm_mode = True


@router.get(
    "/{query_usage_id}",
    response_model=QueryUsageOutput,
    summary="Get Query Usage",
    description="Retrieves a query usage record by its ID for the authenticated user.",
    response_description="The query usage data."
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
    query_usage = service.get_query_usage(db, query_usage_id)
    if not query_usage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Query usage not found or unauthorized access."
        )
    return global_response(query_usage)


@router.get(
    "",
    response_model=List[QueryUsageOutput],
    summary="List All Query Usages",
    description="Lists all query usage records for the authenticated user.",
    response_description="A list of all query usage records."
)
def get_all_query_usages(
    provider: Optional[str] = None,
    duration: Optional[timedelta] = timedelta(hours=24),
    user_id: UUID = Depends(authenticate_user),
    db: Session = Depends(get_db),
    service: QueryUsageService = Depends(get_query_usage_service),
):
    """
    List all query usage records for the authenticated user.

    - **provider**: Optional filter by provider.
    - **duration**: Optional filter by a specific datetime.
    - **user_id**: The authenticated user's ID.
    - **db**: Database session.
    - **service**: QueryUsage service handling business logic.

    Returns:
        List[QueryUsageOutput]: A list of all the user's query usage records.
    """
    query_usages = service.get_all_query_usages(
        db, user_id, provider, duration)
    return global_response(query_usages)
