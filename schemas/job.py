# # schemas/job.py

# from pydantic import BaseModel
# from typing import Optional

# class JobCreate(BaseModel):
#     title: str
#     description: Optional[str] = None
#     company_id: int

# class JobOut(BaseModel):
#     id: int
#     title: str
#     description: Optional[str]
#     company_id: int

#     class Config:
#         from_attributes = True  # Remplace orm_mode dans Pydantic v2
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ----- Sous-schemas -----

class CompanyOut(BaseModel):
    id: int
    company_name: str
    industry: Optional[str]
    creation_year: Optional[str]
    parity_women: Optional[str]
    nb_employees: Optional[str]
    average_age: Optional[str]
    company_url: Optional[str]
    company_description: Optional[str]

    class Config:
        from_attributes = True


class LocationOut(BaseModel):
    id: int
    address: Optional[str]
    local_address: Optional[str]
    city: Optional[str]
    zip_code: Optional[str]
    district: Optional[str]
    latitude: Optional[str]
    longitude: Optional[str]
    country_code: Optional[str]
    local_city: Optional[str]
    local_district: Optional[str]

    class Config:
        from_attributes = True


class MediaOut(BaseModel):
    website: Optional[str]
    linkedin: Optional[str]
    twitter: Optional[str]
    github: Optional[str]
    stackoverflow: Optional[str]
    behance: Optional[str]
    dribbble: Optional[str]
    xing: Optional[str]

    class Config:
        from_attributes = True


class SkillOut(BaseModel):
    skill: str

    class Config:
        from_attributes = True


class ToolOut(BaseModel):
    tool: str

    class Config:
        from_attributes = True


class BenefitOut(BaseModel):
    benefit: str

    class Config:
        from_attributes = True


# ----- Schéma principal Job -----

class JobOut(BaseModel):
    job_reference: str
    wttj_reference: Optional[str]
    poste: Optional[str]
    remote: Optional[str]
    url: Optional[str]
    education_level: Optional[str]
    profile: Optional[str]
    salary_min: Optional[str]
    salary_max: Optional[str]
    salary_currency: Optional[str]
    salary_period: Optional[str]
    published_at: Optional[datetime]
    updated_at: Optional[datetime]
    profession: Optional[str]
    contract_type: Optional[str]
    contract_duration_min: Optional[str]
    contract_duration_max: Optional[str]
    recruitment_process: Optional[str]
    cover_letter: Optional[bool]
    resume: Optional[bool]
    portfolio: Optional[bool]
    picture: Optional[bool]

    company: Optional[CompanyOut]
    location: Optional[LocationOut]
    media: Optional[MediaOut]
    skills: List[SkillOut] = []
    tools: List[ToolOut] = []
    benefits: List[BenefitOut] = []

    class Config:
        from_attributes = True
