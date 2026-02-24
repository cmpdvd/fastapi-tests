import uuid
from datetime import time
from database import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import String
from sqlalchemy.types import UUID
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy import Column, Integer, String, DateTime, func


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    display_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
class Quote(Base):
    __tablename__ = "anecdotes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quote = Column(String, index=True)
    child_name = Column(String, index=True)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

