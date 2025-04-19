from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import analysis, user, settings
from upload import router as upload_router
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Tillåt kommunikation från Flutter-appen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Du kan byta till t.ex. ["http://localhost:5173"] vid behov
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inkludera alla routers
app.include_router(analysis.router)
app.include_router(user.router)
app.include_router(upload_router)
app.include_router(settings.router)

# Serva uppladdade filer
app.mount("/uploaded_files", StaticFiles(directory="uploaded_files"), name="uploaded_files")

@app.get("/")
def root():
    return {"message": "AAS Lab API is running"}
