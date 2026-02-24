from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    display_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
class Anecdote(Base):
    __tablename__ = "anecdotes"

    id = Column(Integer, primary_key=True, index=True)
    quote = Column(String, index=True)
    child_name = Column(String, unique=True, index=True)

