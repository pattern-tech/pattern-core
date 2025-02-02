from fastapi import FastAPI
from dotenv import load_dotenv
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

app.include_router(api_router)

init_db()
