# main_api.py
from fastapi import FastAPI
from api import jobs
from database.db import engine
from database import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="WTTJ Jobs API",
    description="API pour gérer les offres d'emploi",
    version="1.0.0"
)

app.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API WTTJ 🚀"}
