from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from supabase import create_client
import uuid

SUPABASE_URL = "https://yznvfrfaqlljfnbqxzgr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl6bnZmcmZhcWxsamZuYnF4emdyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDUwODc5MDksImV4cCI6MjA2MDY2MzkwOX0.hzjqG-0w8UZdaVoOfQ0ODeMua2TDZDnixRUaoG6ApFU"  # (använd din befintliga API-nyckel)
SUPABASE_BUCKET = "banner-images"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
router = APIRouter()

@router.post("/upload-banner-image")
async def upload_banner_image(file: UploadFile = File(...)):
    try:
        # Generera unikt filnamn
        ext = file.filename.split('.')[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        file_bytes = await file.read()

        # Ladda upp till Supabase Storage
        res = supabase.storage.from_(SUPABASE_BUCKET).upload(filename, file_bytes, {"content-type": file.content_type})
        if res.get("error"):
            raise HTTPException(status_code=500, detail="Upload failed")

        # Hämta public URL
        public_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(filename)
        return {"banner_image_path": public_url}
    except Exception as e:
        print("❌ Banner upload error:", e)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/add-banner")
async def add_banner(data: dict):
    image = data.get("image")
    url = data.get("url")
    if not image or not url:
        raise HTTPException(status_code=400, detail="Missing image or url")
    supabase.table("banners").insert({"image": image, "url": url}).execute()
    return {"message": "Banner added"}

@router.get("/banner-list")
async def get_banners():
    try:
        res = supabase.table("banners").select("*").execute()
        return res.data
    except Exception as e:
        print("❌ Fetch banners error:", e)
        raise HTTPException(status_code=500, detail="Could not fetch banners")
