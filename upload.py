from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.database import SessionLocal
from models import Analysis
import os
import uuid
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 🟢 Servera statiska filer (lägg till i main.py)
# app.mount("/uploaded_files", StaticFiles(directory="uploaded_files"), name="uploaded_files")

@router.post("/upload-analysis")
async def upload_analysis(
    substance: str = Form(...),
    brand: str = Form(...),
    country: str = Form(...),
    expected_amount: str = Form(...),
    actual_amount: str = Form(...),
    uploaded_by: str = Form(...),
    external_link: str = Form(""),
    files: list[UploadFile] = File(...)
):
    db = SessionLocal()
    try:
        saved_paths = []
        for file in files:
            file_ext = file.filename.split('.')[-1]
            unique_filename = f"{uuid.uuid4()}.{file_ext}"
            file_location = os.path.join(UPLOAD_DIR, unique_filename)

            with open(file_location, "wb") as f:
                f.write(await file.read())

            # ✅ Konvertera till URL
            public_url = f"https://aaslab-api.onrender.com/{file_location.replace(os.sep, '/')}"
            saved_paths.append(public_url)

        analysis = Analysis(
            substance=substance,
            brand=brand,
            country=country,
            expected_amount=expected_amount,
            actual_amount=actual_amount,
            uploaded_by=uploaded_by,
            file_paths=";".join(saved_paths),
            external_link=external_link
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


# 🟢 Hämta alla analyser
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
                "file_paths": a.file_paths.split(";") if a.file_paths else []
            })
        return result
    except Exception as e:
        print("❌ GET ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        db.close()
