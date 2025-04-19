from database import Base, engine
from models import User, Analysis, Setting

print("⏳ Creating tables in Supabase...")
Base.metadata.create_all(bind=engine)
print("✅ Done!")
