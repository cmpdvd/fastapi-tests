from pydantic import BaseModel
from uuid import UUID

class UserBase(BaseModel):
    display_name: str | None
    email: str | None

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    pass

class UserRead(UserBase):
    id: UUID
    display_name: str | None
    email: str | None

    class Config:
        from_attributes = True  # allows to read SQLAlchemy objects
