from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import Location

router = APIRouter()

@router.get("/", summary="Liste des localisations")
def get_locations(
    skip: int = Query(0, ge=0, description="Nombre d'éléments à ignorer"),
    limit: int = Query(10, ge=1, le=100, description="Nombre maximum d'éléments"),
    db: Session = Depends(get_db)
):
    locations = (
        db.query(Location)
        .order_by(Location.id)  # OBLIGATOIRE pour MSSQL
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [
        {
            "id": loc.id,
            "address": loc.address,
            "local_address": loc.local_address,
            "city": loc.city,
            "zip_code": loc.zip_code,
            "district": loc.district,
            "latitude": loc.latitude,
            "longitude": loc.longitude,
            "country_code": loc.country_code,
            "local_city": loc.local_city,
            "local_district": loc.local_district
        }
        for loc in locations
    ]
