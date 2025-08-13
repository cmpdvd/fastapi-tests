from pydantic import BaseModel

class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    pass

class UserRead(UserBase):
    id: int

    class Config:
        from_attributes = True  # Permet de lire les objets SQLAlchemy
