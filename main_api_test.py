# main_api_test.py - Version de test sans connexion DB au démarrage
from fastapi import FastAPI
from src.api.routers import jobs, companies, locations, skills, auth

# Commenté temporairement pour tester sans DB
# from src.database.db import engine
# from src.database import models
# models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="WTTJ Jobs API (Test)",
    description="API pour gérer les offres d'emploi - Version de test",
    version="1.0.0-test"
)

app.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
app.include_router(companies.router, prefix="/companies", tags=["Companies"])
app.include_router(locations.router, prefix="/locations", tags=["Locations"])
app.include_router(skills.router, prefix="/skills", tags=["Skills"])
app.include_router(auth.router)


@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API WTTJ (mode test) 🚀"}


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "API is running",
        "mode": "test - no DB connection at startup"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
