from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import SessionLocal
from models import User
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

router = APIRouter()

class RegisterRequest(BaseModel):
    username: str
    password: str

class ChangePasswordRequest(BaseModel):
    username: str
    new_password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class VerifyUserRequest(BaseModel):
    username: str

@router.post("/register")
def register_user(request: RegisterRequest):
    db = SessionLocal()
    try:
        new_user = User(
            username=request.username.lower(),
            password=request.password,
            is_admin=0
        )
        db.add(new_user)
        db.commit()
        return {"message": "User registered successfully"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username already exists")
    finally:
        db.close()

@router.post("/change-password")
def change_password(request: ChangePasswordRequest):
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(username=request.username.lower()).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.password = request.new_password
        db.commit()
        return {"message": "Password changed successfully"}
    finally:
        db.close()

@router.post("/login")
def login_user(request: LoginRequest):
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(username=request.username.lower()).first()
        if not user or user.password != request.password:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        return {
            "message": "Login successful",
            "is_admin": user.is_admin
        }
    finally:
        db.close()

@router.get("/verified-users")
def get_verified_users():
    db = SessionLocal()
    try:
        users = db.query(User).filter_by(is_verified=True).all()
        print("Verified users found:", users)  # Debug-rad
        return [user.username for user in users]
    finally:
        db.close()

@router.post("/verify-user")
def verify_user(request: VerifyUserRequest):
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(username=request.username.lower()).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.is_verified:
            return {"message": "User already verified"}

        user.is_verified = True
        db.commit()
        return {"message": f"{user.username} is now verified"}
    finally:
        db.close()

# ✅ NY: Endpoint för totalantal användare
@router.get("/user-count")
def get_user_count():
    db = SessionLocal()
    try:
        count = db.query(User).count()
        return {"total_users": count}
    except SQLAlchemyError as e:
        print("❌ USER COUNT ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch user count")
    finally:
        db.close()
