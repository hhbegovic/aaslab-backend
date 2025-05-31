from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import uuid
import requests
from app.database import SessionLocal
from models import Banner  # 👈 se till att du har en Banner-modell i models.py
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()

SUPABASE_URL = "yznvfrfaqlljfnbqxzgr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl6bnZmcmZhcWxsamZuYnF4emdyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDUwODc5MDksImV4cCI6MjA2MDY2MzkwOX0.hzjqG-0w8UZdaVoOfQ0ODeMua2TDZDnixRUaoG6ApFU"
SUPABASE_BUCKET = "banner-images"

@router.post("/upload-banner-image")
async def upload_banner_image(file: UploadFile = File(...), url: str = Form(...)):
    try:
        # Skapa unikt filnamn
        ext = file.filename.split('.')[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        file_bytes = await file.read()

        # Ladda upp till Supabase Storage (utan supabase-py)
        response = requests.post(
            f"https://{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{filename}",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            },
            files={"file": (filename, file_bytes, file.content_type)},
        )

        if response.status_code not in [200, 201]:
            print("❌ Upload failed:", response.text)
            raise HTTPException(status_code=500, detail="Failed to upload to Supabase")

        public_url = f"https://{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{filename}"

        # Spara till databas
        db = SessionLocal()
        banner = Banner(image=public_url, url=url)
        db.add(banner)
        db.commit()
        db.close()

        return {"message": "Banner uploaded", "url": public_url}
    except Exception as e:
        print("❌ Banner upload error:", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/banner-list")
def get_banners():
    db = SessionLocal()
    try:
        banners = db.query(Banner).all()
        return [{"id": b.id, "image": b.image, "url": b.url} for b in banners]
    except Exception as e:
        print("❌ Fetch banners error:", e)
        raise HTTPException(status_code=500, detail="Could not fetch banners")
    finally:
        db.close()
