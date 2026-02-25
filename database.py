

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv('DATABASE_URL')

# engine = create_engine(DATABASE_URL)
engine = create_engine(
    DATABASE_URL,
    # Important pour les BIGINT IDENTITY PostgreSQL
    implicit_returning=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


