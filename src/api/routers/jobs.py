from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import Job, Company, Location, Skill, Tool, Benefit, Media
from sqlalchemy.orm import joinedload
from src.api.auth import get_current_user

router = APIRouter()

@router.get("/")
def get_jobs(
    skip: int = Query(0, ge=0, description="Nombre d'éléments à ignorer"),
    limit: int = Query(10, ge=1, le=100, description="Nombre maximum d'éléments à retourner"),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)  # 🔐 PROTECTION ICI
):
    jobs = (
        db.query(Job)
        .options(
            joinedload(Job.company),
            joinedload(Job.location),
            joinedload(Job.skills),
            joinedload(Job.tools),
            joinedload(Job.benefits),
            joinedload(Job.media)
        )
        .order_by(Job.job_reference)
        .offset(skip)
        .limit(limit)
        .all()
    )

    results = []
    for job in jobs:
        results.append({
            "job_reference": job.job_reference,
            "wttj_reference": job.wttj_reference,
            "poste": job.poste,
            "remote": job.remote,
            "url": job.url,
            "education_level": job.education_level,
            "profile": job.profile,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "salary_currency": job.salary_currency,
            "salary_period": job.salary_period,
            "published_at": job.published_at,
            "updated_at": job.updated_at,
            "profession": job.profession,
            "contract_type": job.contract_type,
            "contract_duration_min": job.contract_duration_min,
            "contract_duration_max": job.contract_duration_max,
            "recruitment_process": job.recruitment_process,
            "cover_letter": job.cover_letter,
            "resume": job.resume,
            "portfolio": job.portfolio,
            "picture": job.picture,
            # Company
            "company": {
                "id": job.company.id,
                "name": job.company.name,
                "industry": job.company.industry,
                "creation_year": job.company.creation_year,
                "nb_employees": job.company.nb_employees,
                "average_age": job.company.average_age,
                "url": job.company.url
            } if job.company else None,
            # Location
            "location": {
                "id": job.location.id,
                "city": job.location.city,
                "address": job.location.address,
                "zip_code": job.location.zip_code,
                "country_code": job.location.country_code,
                "latitude": job.location.latitude,
                "longitude": job.location.longitude
            } if job.location else None,
            # Skills
            "skills": [s.skill for s in job.skills] if job.skills else [],
            # Tools
            "tools": [t.tool for t in job.tools] if job.tools else [],
            # Benefits
            "benefits": [b.benefit for b in job.benefits] if job.benefits else [],
            # Media
            "media": {
                "website": job.media.website,
                "linkedin": job.media.linkedin,
                "twitter": job.media.twitter,
                "github": job.media.github,
                "stackoverflow": job.media.stackoverflow,
                "behance": job.media.behance,
                "dribbble": job.media.dribbble,
                "xing": job.media.xing
            } if job.media else None,
        })
    return results
