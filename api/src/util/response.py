from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def global_response(content: dict, metadata: dict = None):
    # Use jsonable_encoder to ensure all objects are JSON serializable
    response_content = {"data": jsonable_encoder(content)}
    if metadata:
        response_content["metadata"] = jsonable_encoder(metadata)
    return JSONResponse(content=response_content)
