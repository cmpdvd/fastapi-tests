from pydantic import BaseModel
from uuid import UUID

# user schemas:
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


# quote schemas:
class QuoteBase(BaseModel):
    quote: str | None
    child_name: str | None

class QuoteCreate(QuoteBase):
    pass

class QuoteUpdate(QuoteBase):
    pass

class QuoteRead(QuoteBase):
    id: UUID
    quote: str | None
    child_name: str | None