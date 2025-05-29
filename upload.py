from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from app.database import SessionLocal
from models import Analysis
from sqlalchemy.exc import SQLAlchemyError
import os
import uuid
import requests

router = APIRouter()

SUPABASE_URL = "yznvfrfaqlljfnbqxzgr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl6bnZmcmZhcWxsamZuYnF4emdyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDUwODc5MDksImV4cCI6MjA2MDY2MzkwOX0.hzjqG-0w8UZdaVoOfQ0ODeMua2TDZDnixRUaoG6ApFU"
SUPABASE_BUCKET = "analysis-files"

@router.post("/upload-analysis")
async def upload_analysis(
    substance: str = Form(...),
    brand: str = Form(...),
    country: str = Form(...),
    expected_amount: str = Form(...),
    actual_amount: str = Form(...),
    uploaded_by: str = Form(...),
    external_link: str = Form(""),
    verification_code: str = Form(None),
    task_number: str = Form(None),
    lab: str = Form(""),  # ✅ NYTT FÄLT
    files: list[UploadFile] = File(...)
):
    db = SessionLocal()
    try:
        saved_paths = []
        for file in files:
            file_ext = file.filename.split('.')[-1]
            unique_filename = f"{uuid.uuid4()}.{file_ext}"
            file_bytes = await file.read()

            response = requests.post(
                f"https://{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{unique_filename}",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                },
                files={"file": (unique_filename, file_bytes, file.content_type)},
            )

            if response.status_code not in [200, 201]:
                print("❌ Upload failed:", response.text)
                raise HTTPException(status_code=500, detail="❌ Failed to upload file to Supabase Storage")

            public_url = f"https://{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{unique_filename}"
            saved_paths.append(public_url)

        analysis = Analysis(
            substance=substance,
            brand=brand,
            country=country,
            expected_amount=expected_amount,
            actual_amount=actual_amount,
            uploaded_by=uploaded_by,
            file_paths=";".join(saved_paths),
            external_link=external_link,
            verification_code=verification_code,
            task_number=task_number,
            lab=lab  # ✅ SPARA I DB
        )

        db.add(analysis)
        db.commit()

        return JSONResponse(content={"message": "Analysis uploaded successfully"}, status_code=200)
    except SQLAlchemyError as e:
        db.rollback()
        print("❌ DB ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        print("❌ GENERAL ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        db.close()


@router.get("/analyses")
def get_all_analyses():
    db = SessionLocal()
    try:
        analyses = db.query(Analysis).all()
        result = []
        for a in analyses:
            result.append({
                "id": a.id,
                "substance": a.substance,
                "brand": a.brand,
                "country": a.country,
                "expected_amount": a.expected_amount,
                "actual_amount": a.actual_amount,
                "uploaded_by": a.uploaded_by,
                "external_link": a.external_link,
                "verification_code": a.verification_code,
                "task_number": a.task_number,
                "lab": a.lab,  # ✅ RETURNERA LAB
                "file_paths": a.file_paths.split(";") if a.file_paths else []
            })
        return result
    except Exception as e:
        print("❌ GET ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        db.close()


@router.delete("/delete-analysis/{analysis_id}")
def delete_analysis(analysis_id: int):
    db = SessionLocal()
    try:
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        file_urls = analysis.file_paths.split(";") if analysis.file_paths else []
        filenames = [url.split("/")[-1] for url in file_urls]

        delete_response = requests.post(
            f"https://{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/remove",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            },
            json={"prefixes": filenames}
        )

        if delete_response.status_code not in [200, 204]:
            print("❌ Failed to delete files:", delete_response.text)

        db.delete(analysis)
        db.commit()
        return JSONResponse(content={"message": "Analysis and files deleted"}, status_code=200)
    except Exception as e:
        print("❌ DELETE ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Failed to delete analysis")
    finally:
        db.close()
