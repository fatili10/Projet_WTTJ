from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db
from database import models
from schemas.job import JobOut, JobCreate

router = APIRouter()

@router.get("/", response_model=list[JobOut])
def get_all_jobs(db: Session = Depends(get_db)):
    return db.query(models.Job).all()

@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job non trouvé")
    return job

