from pydantic import BaseModel
from typing import List, Optional

# För att ta emot och returnera analysdata
class AnalysisBase(BaseModel):
    substance: str
    brand: str
    country: str
    expected_amount: str
    actual_amount: str
    uploaded_by: str
    file_paths: List[str]
    external_link: Optional[str] = None

class AnalysisCreate(AnalysisBase):
    pass

class AnalysisOut(AnalysisBase):
    id: int

    class Config:
        orm_mode = True


# För användarregistrering och inloggning
class UserBase(BaseModel):
    username: str
    password: str

class UserCreate(UserBase):
    pass

class UserOut(BaseModel):
    id: int
    username: str
    is_admin: int

    class Config:
        orm_mode = True
