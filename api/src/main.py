from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.openapi.utils import get_openapi
from scalar_fastapi.scalar_fastapi import Layout
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

from src import api_router
from src.db.models import init_db

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
