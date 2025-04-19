from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Ange din PostgreSQL-URL här
DATABASE_URL = "postgresql://admin:Ha93ja94@localhost/aaslab"

# Skapa databasmotor
engine = create_engine(DATABASE_URL)

# Skapar sessionsinstans
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Basmodell för tabeller
Base = declarative_base()
