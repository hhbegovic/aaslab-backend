from fastapi import FastAPI
from routers import analysis, user
from upload import router as upload_router  # <-- NY RAD
from fastapi.middleware.cors import CORSMiddleware
from routers import settings
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
app.include_router(upload_router)  # <-- NY RAD
app.include_router(settings.router)
app.mount("/uploaded_files", StaticFiles(directory="uploaded_files"), name="uploaded_files")
