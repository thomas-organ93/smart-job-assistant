import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

DB_NAME = os.environ.get("POSTGRES_DB_USER")
DB_PASSWORD = os.environ.get("POSTGRES_DB_PASSWORD")

# Grab the exact host name from your environment file, default to standard localhost
db_host = os.environ.get('DB_HOST', 'localhost')

DATABASE_URL = f"postgresql://{DB_NAME}:{DB_PASSWORD}@{db_host}:5432/graduate_jobs"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()