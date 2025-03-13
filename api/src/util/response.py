from pydantic import BaseModel
from pydantic.generics import GenericModel
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import TypeVar, Generic, Optional, Any

DataT = TypeVar("DataT")
MetadataT = TypeVar("MetadataT")


class GlobalResponse(GenericModel, Generic[DataT, MetadataT]):
    data: DataT
    metadata: Optional[MetadataT] = None


def global_response(content: dict, metadata: dict = None):
    # Use jsonable_encoder to ensure all objects are JSON serializable
    response_content = {"data": jsonable_encoder(content)}
    if metadata:
        response_content["metadata"] = jsonable_encoder(metadata)
    else:
        response_content["metadata"] = {}

    return JSONResponse(content=response_content)


class ExceptionResponse(BaseModel):
    detail: str
