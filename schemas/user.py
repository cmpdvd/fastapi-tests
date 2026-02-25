from pydantic import BaseModel


class UserBase(BaseModel):
    display_name: str | None
    email: str | None


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    pass


class UserRead(UserBase):
    id: int
    display_name: str | None
    email: str | None
    class Config:
        from_attributes = True  # allows to read SQLAlchemy objects
