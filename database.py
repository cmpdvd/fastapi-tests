

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# DATABASE_URL = "postgresql://userdc:passworddc@localhost:5432/dbdc"
DATABASE_URL = "postgresql://postgres:splgiJFbXLyOwuWwQeascrFjFDheoJtV@postgres.railway.internal:5432/railway"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


