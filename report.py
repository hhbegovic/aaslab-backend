from fastapi import APIRouter, Request, HTTPException
import smtplib
from email.message import EmailMessage

router = APIRouter()

# Din konfiguration (redan anpassad)
ADMIN_EMAIL = "aaslabarchive@proton.me"
SMTP_USERNAME = "harishbegovic93@gmail.com"
SMTP_PASSWORD = "wqvknjgrquconvyl"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

@router.post("/report-analysis")
async def report_analysis(request: Request):
    data = await request.json()
    analysis_id = data.get("analysis_id")
    substance = data.get("substance")
    uploaded_by = data.get("uploaded_by")

    if not analysis_id or not substance or not uploaded_by:
        raise HTTPException(status_code=400, detail="Missing fields")

    try:
        msg = EmailMessage()
        msg["Subject"] = f"🚩 Analysis Reported: ID {analysis_id}"
        msg["From"] = SMTP_USERNAME
        msg["To"] = ADMIN_EMAIL
        msg.set_content(
            f"An analysis has been reported:\n\n"
            f"ID: {analysis_id}\n"
            f"Substance: {substance}\n"
            f"Uploaded by: {uploaded_by}\n\n"
            f"Check AAS Lab Archive for details."
        )

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)

        return {"message": "Report sent successfully"}
    except Exception as e:
        print("❌ Email error:", e)
        raise HTTPException(status_code=500, detail="Failed to send report email")
