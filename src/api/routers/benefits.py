from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import Benefit

router = APIRouter()

@router.get("/", summary="Liste des avantages")
def get_benefits(
    skip: int = Query(0, ge=0, description="Nombre d'elements a ignorer"),
    limit: int = Query(10, ge=1, le=100, description="Nombre maximum d'elements"),
    db: Session = Depends(get_db)
):
    benefits = (
        db.query(Benefit)
        .order_by(Benefit.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [
        {
            "id": b.id,
            "benefit": b.benefit,
            "job_reference": b.job_reference
        }
        for b in benefits
    ]
