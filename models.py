from sqlalchemy import Column, Integer, String, Text, Boolean
from app.database import Base

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    substance = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    country = Column(String, nullable=False)
    expected_amount = Column(String, nullable=False)
    actual_amount = Column(String, nullable=False)
    uploaded_by = Column(String, nullable=False)
    file_paths = Column(Text, nullable=False)
    external_link = Column(String, nullable=True)
    lab = Column(String, nullable=True)  # ✅ SAKNAS I DIN – nu tillagd
    verification_code = Column(String, nullable=True)
    task_number = Column(String, nullable=True)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_admin = Column(Integer, default=0)
    is_verified = Column(Boolean, default=False)

class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    btc_address = Column(Text)
    contact_email = Column(Text)
    banner_url = Column(Text)
    banner_image_path = Column(Text)
    banner_list = Column(Text)

class Banner(Base):
    __tablename__ = "banners"

    id = Column(Integer, primary_key=True, index=True)
    image = Column(String, nullable=False)
    url = Column(String, nullable=False)
