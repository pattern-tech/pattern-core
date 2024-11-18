from fastapi.responses import JSONResponse


def global_response(content: dict, metadata: dict = None):
    response_content = {"data": content}
    if metadata:
        response_content["metadata"] = metadata
    return JSONResponse(content=response_content)
