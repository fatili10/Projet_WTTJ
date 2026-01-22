"""
Script pour ajouter les donnees manquantes depuis data.csv
"""
import pandas as pd
import sys
import os
from datetime import datetime
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.database.db import engine
from src.database.models import Company, Location, Job, Media, Skill, Tool, Benefit


def parse_datetime(dt_str):
    if pd.isna(dt_str) or not dt_str:
        return None
    try:
        return pd.to_datetime(dt_str)
    except Exception:
        return None


def parse_int(value):
    if pd.isna(value) or value == '':
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def parse_float(value):
    if pd.isna(value) or value == '':
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def parse_bool(value):
    if pd.isna(value) or value == '':
        return None
    value_str = str(value).lower()
    if value_str in ['true', 'mandatory', 'optional', 'enabled']:
        return True
    if value_str in ['false', 'disabled']:
        return False
    return None


def safe_get(row, key):
    value = row.get(key)
    if pd.isna(value):
        return None
    return value


def add_missing_data():
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        print("Chargement de data.csv...")
        df = pd.read_csv('data/data.csv')
        print(f"Lignes dans CSV: {len(df)}")

        df = df.replace({pd.NA: None, pd.NaT: None})
        df = df.where(pd.notna(df), None)

        # Recuperer les job_reference existants
        existing_jobs = set(
            r[0] for r in session.query(Job.job_reference).all()
        )
        print(f"Jobs existants en base: {len(existing_jobs)}")

        company_cache = {}
        location_cache = {}

        # Charger les companies et locations existantes dans le cache
        for company in session.query(Company).all():
            company_cache[company.name] = company
        for location in session.query(Location).all():
            location_cache[f"{location.city}_{location.zip_code}"] = location

        added_jobs = 0
        added_skills = 0
        added_tools = 0
        added_benefits = 0

        print("\nAjout des donnees manquantes...")
        for idx, row in df.iterrows():
            if idx % 500 == 0:
                print(f"Traitement ligne {idx}/{len(df)}...")

            job_ref = safe_get(row, 'job_reference')
            if not job_ref or job_ref in existing_jobs:
                continue  # Skip si pas de reference ou deja existant

            # 1. Company
            company_name = safe_get(row, 'company_name')
            if company_name and company_name not in company_cache:
                company = session.query(Company).filter_by(name=company_name).first()
                if not company:
                    company = Company(
                        name=company_name,
                        industry=safe_get(row, 'industry'),
                        creation_year=parse_int(safe_get(row, 'creation_year')),
                        parity_women=safe_get(row, 'parity_women'),
                        nb_employees=parse_int(safe_get(row, 'nb_employees')),
                        average_age=parse_float(safe_get(row, 'average_age')),
                        url=safe_get(row, 'company_url'),
                        description=safe_get(row, 'company_description')
                    )
                    session.add(company)
                    session.flush()
                company_cache[company_name] = company

            company = company_cache.get(company_name)

            # 2. Location
            city = safe_get(row, 'city')
            zip_code = safe_get(row, 'zip_code')
            location_key = f"{city}_{zip_code}"
            if city and location_key not in location_cache:
                location = session.query(Location).filter_by(
                    city=city,
                    zip_code=zip_code
                ).first()
                if not location:
                    location = Location(
                        address=safe_get(row, 'address'),
                        local_address=safe_get(row, 'local_address'),
                        city=city,
                        zip_code=zip_code,
                        district=safe_get(row, 'district'),
                        latitude=parse_float(safe_get(row, 'latitude')),
                        longitude=parse_float(safe_get(row, 'longitude')),
                        country_code=safe_get(row, 'country_code'),
                        local_city=safe_get(row, 'local_city'),
                        local_district=safe_get(row, 'local_district')
                    )
                    session.add(location)
                    session.flush()
                location_cache[location_key] = location

            location = location_cache.get(location_key)

            # 3. Job
            job = Job(
                job_reference=job_ref,
                wttj_reference=safe_get(row, 'wttj_reference'),
                poste=safe_get(row, 'poste'),
                remote=safe_get(row, 'remote'),
                url=safe_get(row, 'url'),
                education_level=safe_get(row, 'education_level'),
                profile=safe_get(row, 'profile'),
                salary_min=parse_int(safe_get(row, 'salary_min')),
                salary_max=parse_int(safe_get(row, 'salary_max')),
                salary_currency=safe_get(row, 'salary_currency'),
                salary_period=safe_get(row, 'salary_period'),
                published_at=parse_datetime(safe_get(row, 'published_at')),
                updated_at=parse_datetime(safe_get(row, 'updated_at')),
                profession=safe_get(row, 'profession'),
                contract_type=safe_get(row, 'contract_type'),
                contract_duration_min=safe_get(row, 'contract_duration_min'),
                contract_duration_max=safe_get(row, 'contract_duration_max'),
                recruitment_process=safe_get(row, 'recruitment_process'),
                cover_letter=parse_bool(safe_get(row, 'cover_letter')),
                resume=parse_bool(safe_get(row, 'resume')),
                portfolio=parse_bool(safe_get(row, 'portfolio')),
                picture=parse_bool(safe_get(row, 'picture')),
                company_id=company.id if company else None,
                location_id=location.id if location else None
            )
            session.add(job)
            added_jobs += 1

            # 4. Media
            media = Media(
                job_reference=job_ref,
                website=safe_get(row, 'media_website'),
                linkedin=safe_get(row, 'media_linkedin'),
                twitter=safe_get(row, 'media_twitter'),
                github=safe_get(row, 'media_github'),
                stackoverflow=safe_get(row, 'media_stackoverflow'),
                behance=safe_get(row, 'media_behance'),
                dribbble=safe_get(row, 'media_dribbble'),
                xing=safe_get(row, 'media_xing')
            )
            session.add(media)

            # 5. Skills
            skills_str = safe_get(row, 'skills')
            if skills_str and str(skills_str).strip():
                for skill_name in str(skills_str).split(','):
                    skill_name = skill_name.strip()
                    if skill_name:
                        session.add(Skill(job_reference=job_ref, skill=skill_name))
                        added_skills += 1

            # 6. Tools
            tools_str = safe_get(row, 'tools')
            if tools_str and str(tools_str).strip():
                for tool_name in str(tools_str).split(','):
                    tool_name = tool_name.strip()
                    if tool_name:
                        session.add(Tool(job_reference=job_ref, tool=tool_name))
                        added_tools += 1

            # 7. Benefits
            benefits_str = safe_get(row, 'benefits')
            if benefits_str and str(benefits_str).strip():
                for benefit_name in str(benefits_str).split(','):
                    benefit_name = benefit_name.strip()
                    if benefit_name:
                        session.add(Benefit(job_reference=job_ref, benefit=benefit_name))
                        added_benefits += 1

            # Ajouter au set pour eviter doublons dans cette session
            existing_jobs.add(job_ref)

        print("\nEnregistrement en base...")
        session.commit()

        print("\n=== RESUME ===")
        print(f"Jobs ajoutes: {added_jobs}")
        print(f"Skills ajoutes: {added_skills}")
        print(f"Tools ajoutes: {added_tools}")
        print(f"Benefits ajoutes: {added_benefits}")

        print("\n=== TOTAUX EN BASE ===")
        print(f"Jobs: {session.query(Job).count()}")
        print(f"Skills: {session.query(Skill).count()}")
        print(f"Tools: {session.query(Tool).count()}")
        print(f"Benefits: {session.query(Benefit).count()}")

    except Exception as e:
        print(f"\nERREUR: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    add_missing_data()
