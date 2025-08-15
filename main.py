from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from database import Base, engine
from fastapi import HTTPException
import schemas
import models
from deps import get_db

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from Railway & FastAPI David!"}

@app.get("/users/", response_model=list[schemas.UserRead])
def read_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

@app.get("/users/{user_id}", response_model=schemas.UserRead)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user_to_get = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_to_get:
        raise HTTPException(status_code=404, detail="User not found")
    return user_to_get

@app.post("/users", response_model=schemas.UserRead)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    new_user = models.User(name=user.name, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.delete("/users/{user_id}", response_model=schemas.UserRead)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user_to_delete = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user_to_delete)
    db.commit()
    return user_to_delete

@app.put("/users/{user_id}", response_model=schemas.UserRead)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    user_to_update = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_to_update:
        raise HTTPException(status_code=404, detail="User not found")
    user_to_update.name = user.name
    user_to_update.email = user.email
    db.commit()
    db.refresh(user_to_update)
    return user_to_update