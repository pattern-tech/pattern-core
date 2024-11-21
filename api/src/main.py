from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src import api_router
from src.db.models import init_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

init_db()
