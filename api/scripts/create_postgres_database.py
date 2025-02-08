#!/usr/bin/env python3
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2 import sql
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get connection settings from environment variables
db_host = os.environ.get('POSTGRES_HOST', 'localhost')
db_port = os.environ.get('POSTGRES_PORT', '5432')
db_user = os.environ.get('POSTGRES_USERNAME')
db_password = os.environ.get('POSTGRES_PASSWORD')
target_db = os.environ.get('POSTGRES_DB')

if not all([db_user, db_password, target_db]):
    raise ValueError(
        "Ensure POSTGRES_USERNAME, POSTGRES_PASSWORD, and POSTGRES_DB are set in the environment.")

try:
    # Connect to the default database (usually 'postgres')
    conn = psycopg2.connect(
        dbname='postgres',  # default database
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    # Check if the target database already exists
    cursor.execute(
        "SELECT 1 FROM pg_database WHERE datname = %s", (target_db,))
    exists = cursor.fetchone()

    if exists:
        print(f"Database '{target_db}' already exists.")
    else:
        # Create the database if it does not exist using Identifier for proper quoting
        create_db_query = sql.SQL("CREATE DATABASE {}").format(
            sql.Identifier(target_db))
        cursor.execute(create_db_query)
        print(f"Database '{target_db}' created successfully.")

    # Clean up
    cursor.close()
    conn.close()

except Exception as error:
    print("An error occurred while creating the database:", error)
