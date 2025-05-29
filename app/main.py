from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import analysis, user, settings
from upload import router as upload_router
from routers.report_analysis import router as report_router
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis.router)
app.include_router(user.router)
app.include_router(settings.router)
app.include_router(upload_router)
app.include_router(report_analysis.router)

app.mount("/uploaded_files", StaticFiles(directory="uploaded_files"), name="uploaded_files")

@app.get("/")
def root():
    return {"message": "AAS Lab API is running"}
