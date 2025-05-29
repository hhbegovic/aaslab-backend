from fastapi import APIRouter, Request
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText

router = APIRouter()

class ReportRequest(BaseModel):
    analysisId: int
    substance: str
    brand: str

@router.post("/report")
async def report_analysis(report: ReportRequest):
    msg = MIMEText(
        f"🚨 A report has been submitted for:\n\n"
        f"Analysis ID: {report.analysisId}\n"
        f"Substance: {report.substance}\n"
        f"Brand: {report.brand}"
    )
    msg["Subject"] = f"🧪 Reported Analysis ID {report.analysisId}"
    msg["From"] = "harishbegovic93@gmail.com"
    msg["To"] = "aaslabarchive@proton.me"

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login("harishbegovic93@gmail.com", "wqvknjgrquconvyl")
            server.sendmail(msg["From"], [msg["To"]], msg.as_string())
        return {"message": "Report sent successfully"}
    except Exception as e:
        print("❌ Email send failed:", e)
        return {"error": "Failed to send report"}
