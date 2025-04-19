from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Render sätter miljövariabler automatiskt – inget behov av load_dotenv
DATABASE_URL = os.environ.get("DATABASE_URL")

# Kontrollera att URL är korrekt
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
