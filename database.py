

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv('DATABASE_URL')
print("DEBUG database.py DATABASE_URL =", DATABASE_URL) # check if DATABASE_URL is set


# DATABASE_URL = "postgresql://userdc:passworddc@localhost:5432/dbdc"
# DATABASE_URL = "postgresql://userdc:passworddc@postgres.railway.internal:5432/dbdc" # ok
# DATABASE_URL = "postgresql://userdc:passworddc@postgres.railway.internal:5432/railway"
# DATABASE_URL = "postgresql://postgres:splgiJFbXLyOwuWwQeascrFjFDheoJtV@postgres.railway.internal:5432/railway"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


