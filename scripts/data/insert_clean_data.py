"""
Script d'insertion des données nettoyées dans la base SQL Azure
"""
import pandas as pd
import sys
import os
from datetime import datetime
from sqlalchemy.orm import sessionmaker

# Ajouter le chemin racine au PYTHONPATH
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, ROOT_DIR)

from src.database.db import engine
from src.database.models import Base, Company, Location, Job, Media, Skill, Tool, Benefit


def parse_datetime(dt_str):
    """Parse datetime string to datetime object"""
    if pd.isna(dt_str) or not dt_str:
        return None
    try:
        return pd.to_datetime(dt_str)
    except Exception:
        return None


def parse_int(value):
    """Parse integer value safely"""
    if pd.isna(value) or value == '':
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def parse_float(value):
    """Parse float value safely"""
    if pd.isna(value) or value == '':
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def parse_bool(value):
    """Parse boolean value from string"""
    if pd.isna(value) or value == '':
        return None
    value_str = str(value).lower()
    if value_str in ['true', 'mandatory', 'optional', 'enabled']:
        return True
    if value_str in ['false', 'disabled']:
        return False
    return None


def safe_get(row, key):
    """Get value from row, return None if NaN"""
    value = row.get(key)
    if pd.isna(value):
        return None
    return value


def insert_data():
    # Créer la session
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        print("Chargement du fichier CSV...")
        df = pd.read_csv(os.path.join(ROOT_DIR, 'data', 'archive', 'jobs_clean_20260217_174627.csv'))
        print(f"Nombre de lignes chargees: {len(df)}")

        # Remplacer NaN par None
        df = df.replace({pd.NA: None, pd.NaT: None})
        df = df.where(pd.notna(df), None)

        company_cache = {}
        location_cache = {}

        print("\nInsertion des donnees...")
        for idx, row in df.iterrows():
            if idx % 100 == 0:
                print(f"Traitement ligne {idx}/{len(df)}...")

            # 1. Gérer l'entreprise
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
                    session.flush()  # Pour obtenir l'ID
                company_cache[company_name] = company

            company = company_cache.get(company_name)

            # 2. Gérer la localisation
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

            # 3. Créer le job
            job_ref = safe_get(row, 'job_reference')
            if not job_ref:
                continue

            # Vérifier si le job existe déjà
            existing_job = session.query(Job).filter_by(job_reference=job_ref).first()
            if existing_job:
                continue  # Skip si déjà existant

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
            session.flush()

            # 4. Ajouter les médias
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

            # 5. Ajouter les skills
            skills_str = safe_get(row, 'skills')
            if skills_str and str(skills_str).strip():
                for skill_name in str(skills_str).split(','):
                    skill_name = skill_name.strip()
                    if skill_name:
                        skill = Skill(
                            job_reference=job_ref,
                            skill=skill_name
                        )
                        session.add(skill)

            # 6. Ajouter les tools
            tools_str = safe_get(row, 'tools')
            if tools_str and str(tools_str).strip():
                for tool_name in str(tools_str).split(','):
                    tool_name = tool_name.strip()
                    if tool_name:
                        tool = Tool(
                            job_reference=job_ref,
                            tool=tool_name
                        )
                        session.add(tool)

            # 7. Ajouter les benefits
            benefits_str = safe_get(row, 'benefits')
            if benefits_str and str(benefits_str).strip():
                for benefit_name in str(benefits_str).split(','):
                    benefit_name = benefit_name.strip()
                    if benefit_name:
                        benefit = Benefit(
                            job_reference=job_ref,
                            benefit=benefit_name
                        )
                        session.add(benefit)

            # Commit par batch de 50 lignes
            if idx % 50 == 0 and idx > 0:
                session.commit()
                print(f"  Batch commit a la ligne {idx}")

        # Commit final pour les dernières lignes
        print("\nEnregistrement en base de donnees...")
        session.commit()
        print("Insertion terminee avec succes!")

        # Statistiques
        print("\n=== STATISTIQUES ===")
        print(f"Companies: {session.query(Company).count()}")
        print(f"Locations: {session.query(Location).count()}")
        print(f"Jobs: {session.query(Job).count()}")
        print(f"Skills: {session.query(Skill).count()}")
        print(f"Tools: {session.query(Tool).count()}")
        print(f"Benefits: {session.query(Benefit).count()}")
        print(f"Media: {session.query(Media).count()}")

    except Exception as e:
        print(f"\nERREUR: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    insert_data()
