from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import SessionLocal
from models import User
from sqlalchemy.orm import Session

router = APIRouter()

class PasswordChangeRequest(BaseModel):
    username: str
    new_password: str

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username.lower()).first()

@router.post("/change-password")
def change_password(request: PasswordChangeRequest):
    db = SessionLocal()
    user = get_user_by_username(db, request.username)

    if not user:
        db.close()
        raise HTTPException(status_code=404, detail="User not found")

    user.password = request.new_password
    db.commit()
    db.close()

    return {"message": "Password updated successfully"}
