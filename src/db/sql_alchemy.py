import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()
Base = declarative_base()


class Database:
    def __init__(self):
        username = os.environ.get("POSTGRES_USERNAME")
        password = os.environ.get("POSTGRES_PASSWORD")
        host = os.environ.get("POSTGRES_HOST")
        port = os.environ.get("POSTGRES_PORT")
        database = os.environ.get("POSTGRES_DB")
        DATABASE_URL = (
            f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
        )

        self.engine = create_engine(DATABASE_URL)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def init_db(self):
        Base.metadata.create_all(bind=self.engine)

    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
