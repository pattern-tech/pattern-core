import os
import sentry_sdk

from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from scalar_fastapi.scalar_fastapi import Layout
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference
from fastapi import FastAPI, Request, HTTPException, status

from src import api_router
from src.db.models import init_db
from src.share.logging import Logging

load_dotenv()
_logger = Logging().get_logger()

if os.environ.get("SENTRY_DNS"):
    # Initialize Sentry with your DSN
    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DNS"),
        # Add data like request headers and IP for users,
        # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
        send_default_pii=True,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for tracing.
        traces_sample_rate=1.0,
        _experiments={
            # Set continuous_profiling_auto_start to True
            # to automatically start the profiler on when
            # possible.
            "continuous_profiling_auto_start": True,
        },
    )

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global handler for all exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):

    # Send the exception to Sentry
    if os.environ.get("SENTRY_DSN"):
        sentry_sdk.capture_exception(exc)

    # You can customize the response based on the exception type
    if isinstance(exc, HTTPException):
        _logger.error(
            f"[{request.method}] {request.url} - {exc.status_code} - {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    # For any other exceptions, return a 500 error
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Something went wrong"},
    )


@app.get("/api-doc", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Pattern-Core API",
        hide_models=True,
        layout=Layout.MODERN
    )


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Pattern-Core API",
        version="1.0.0",
        description="Pattern Core API Documentation for creating user, workspace, project, tool, and conversation.",
        routes=app.routes,
    )

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

app.include_router(api_router)

init_db()
