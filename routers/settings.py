from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from app.database import SessionLocal
from models import Setting
import os
import shutil
import json

router = APIRouter()

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class SettingsUpdateRequest(BaseModel):
    btc_address: str
    contact_email: str
    banner_url: str
    banner_image_path: str

class BannerItem(BaseModel):
    image: str
    url: str

@router.get("/settings")
def get_settings():
    db = SessionLocal()
    try:
        settings = db.query(Setting).first()
        if not settings:
            raise HTTPException(status_code=404, detail="Settings not found")
        return {
            "btc_address": settings.btc_address or "",
            "contact_email": settings.contact_email or "",
            "banner_url": settings.banner_url or "",
            "banner_image_path": settings.banner_image_path or "",
            "banner_list": json.loads(settings.banner_list or "[]")
        }
    finally:
        db.close()

@router.post("/update-settings")
def update_settings(data: SettingsUpdateRequest):
    db = SessionLocal()
    try:
        settings = db.query(Setting).first()
        if settings:
            settings.btc_address = data.btc_address
            settings.contact_email = data.contact_email
            settings.banner_url = data.banner_url
            settings.banner_image_path = data.banner_image_path
        else:
            settings = Setting(
                btc_address=data.btc_address,
                contact_email=data.contact_email,
                banner_url=data.banner_url,
                banner_image_path=data.banner_image_path
            )
            db.add(settings)
        db.commit()
        return {"message": "Settings updated"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update settings")
    finally:
        db.close()

@router.post("/upload-banner-image")
def upload_banner_image(file: UploadFile = File(...)):
    try:
        filename = f"banner_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        url = f"https://aaslab-api.onrender.com/uploaded_files/{filename}"
        return {"banner_image_path": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")

@router.get("/banner-list")
def get_banner_list():
    db = SessionLocal()
    try:
        settings = db.query(Setting).first()
        if not settings:
            return []
        return json.loads(settings.banner_list or "[]")
    finally:
        db.close()

@router.post("/add-banner")
def add_banner(item: BannerItem):
    db = SessionLocal()
    try:
        settings = db.query(Setting).first()
        if not settings:
            settings = Setting(banner_list=json.dumps([]))
            db.add(settings)
            db.commit()
            db.refresh(settings)

        banners = json.loads(settings.banner_list or "[]")
        banners.append(item.dict())
        settings.banner_list = json.dumps(banners)
        db.commit()
        return {"message": "Banner added"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to add banner: {e}")
    finally:
        db.close()

@router.post("/delete-banner")
def delete_banner(item: BannerItem):
    db = SessionLocal()
    try:
        settings = db.query(Setting).first()
        if not settings:
            raise HTTPException(status_code=404, detail="Settings not found")

        banners = json.loads(settings.banner_list or "[]")
        banners = [b for b in banners if b["image"] != item.image or b["url"] != item.url]
        settings.banner_list = json.dumps(banners)
        db.commit()
        return {"message": "Banner deleted"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete banner: {e}")
    finally:
        db.close()
