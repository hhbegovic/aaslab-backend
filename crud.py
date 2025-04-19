from sqlalchemy.orm import Session
from models import Analysis, User
from schemas import AnalysisCreate, UserCreate
from typing import List

# ANALYS-FUNKTIONER

def get_all_analyses(db: Session) -> List[Analysis]:
    return db.query(Analysis).all()

def create_analysis(db: Session, analysis: AnalysisCreate) -> Analysis:
    db_analysis = Analysis(
        substance=analysis.substance,
        brand=analysis.brand,
        country=analysis.country,
        expected_amount=analysis.expected_amount,
        actual_amount=analysis.actual_amount,
        uploaded_by=analysis.uploaded_by,
        file_paths=",".join(analysis.file_paths),
        external_link=analysis.external_link,
    )
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    return db_analysis


# ANVÄNDAR-FUNKTIONER

def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(username=user.username.lower(), password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = get_user_by_username(db, username.lower())
    if user and user.password == password:
        return user
    return None
