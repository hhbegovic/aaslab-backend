from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, analyses

app = FastAPI()

# Tillåt kommunikation från Flutter-appen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Du kan byta till t.ex. ["http://localhost:5173"] vid behov
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inkludera router-filerna
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(analyses.router, prefix="/analyses", tags=["Analyses"])

@app.get("/")
def root():
    return {"message": "AAS Lab API is running"}
