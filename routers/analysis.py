from fastapi import APIRouter, HTTPException
from app.database import SessionLocal
from models import Analysis
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel

router = APIRouter()

@router.get("/ping")
async def ping():
    return {"message": "pong"}

@router.get("/analyses")
def get_all_analyses():
    db = SessionLocal()
    try:
        analyses = db.query(Analysis).all()
        return [
            {
                "id": analysis.id,
                "substance": analysis.substance,
                "brand": analysis.brand,
                "country": analysis.country,
                "expected_amount": analysis.expected_amount,
                "actual_amount": analysis.actual_amount,
                "uploaded_by": analysis.uploaded_by,
                "external_link": analysis.external_link,
                "file_paths": analysis.file_paths.split(";") if analysis.file_paths else [],
                "lab": analysis.lab,
                "verification_code": analysis.verification_code,
                "task_number": analysis.task_number,
                "pip_count": analysis.pip_count,
                "nopip_count": analysis.nopip_count,
            }
            for analysis in analyses
        ]
    except SQLAlchemyError as e:
        print("❌ GET ANALYSES ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve analyses")
    finally:
        db.close()

@router.delete("/delete-analysis/{analysis_id}")
def delete_analysis(analysis_id: int):
    db = SessionLocal()
    try:
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        db.delete(analysis)
        db.commit()
        return {"message": "Analysis deleted"}
    except SQLAlchemyError as e:
        db.rollback()
        print("❌ DELETE ANALYSIS ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Failed to delete analysis")
    finally:
        db.close()

# -------------------------------
# ✅ NEW: Vote on analysis (Pip / No Pip)
# -------------------------------
class VoteRequest(BaseModel):
    analysisId: int
    vote: str  # "pip" or "nopip"

@router.post("/vote-analysis")
def vote_analysis(data: VoteRequest):
    db = SessionLocal()
    try:
        analysis = db.query(Analysis).filter(Analysis.id == data.analysisId).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        if data.vote == "pip":
            analysis.pip_count += 1
        elif data.vote == "nopip":
            analysis.nopip_count += 1
        else:
            raise HTTPException(status_code=400, detail="Invalid vote type")

        db.commit()
        return {"success": True, "vote": data.vote}
    except SQLAlchemyError as e:
        db.rollback()
        print("❌ VOTE ANALYSIS ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Failed to record vote")
    finally:
        db.close()
