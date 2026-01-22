from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import Skill

router = APIRouter()

@router.get("/", summary="Liste des compétences")
def get_skills(
    skip: int = Query(0, ge=0, description="Nombre d'éléments à ignorer"),
    limit: int = Query(10, ge=1, le=100, description="Nombre maximum d'éléments"),
    db: Session = Depends(get_db)
):
    skills = (
        db.query(Skill)
        .order_by(Skill.id)  # OBLIGATOIRE pour MSSQL
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [
        {
            "id": s.id,
            "skill": s.skill,
            "job_reference": s.job_reference
        }
        for s in skills
    ]
