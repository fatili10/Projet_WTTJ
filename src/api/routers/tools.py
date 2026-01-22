from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import Tool

router = APIRouter()

@router.get("/", summary="Liste des outils")
def get_tools(
    skip: int = Query(0, ge=0, description="Nombre d'elements a ignorer"),
    limit: int = Query(10, ge=1, le=100, description="Nombre maximum d'elements"),
    db: Session = Depends(get_db)
):
    tools = (
        db.query(Tool)
        .order_by(Tool.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [
        {
            "id": t.id,
            "tool": t.tool,
            "job_reference": t.job_reference
        }
        for t in tools
    ]
