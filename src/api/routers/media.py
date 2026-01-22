from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import Media

router = APIRouter()

@router.get("/", summary="Liste des medias sociaux")
def get_media(
    skip: int = Query(0, ge=0, description="Nombre d'elements a ignorer"),
    limit: int = Query(10, ge=1, le=100, description="Nombre maximum d'elements"),
    db: Session = Depends(get_db)
):
    media_list = (
        db.query(Media)
        .order_by(Media.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [
        {
            "id": m.id,
            "job_reference": m.job_reference,
            "website": m.website,
            "linkedin": m.linkedin,
            "twitter": m.twitter,
            "github": m.github,
            "stackoverflow": m.stackoverflow,
            "behance": m.behance,
            "dribbble": m.dribbble,
            "xing": m.xing
        }
        for m in media_list
    ]
