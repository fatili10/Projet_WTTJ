# import pandas as pd
# from datetime import datetime
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from database.models import Base, Company, Job, Tag, Location, Language
# import numpy as np
# from dotenv import load_dotenv
# import os

# load_dotenv()




# # from nettoyage import fix_nan_in_job
# # Connexion à la base (à adapter avec tes identifiants)
# DATABASE_URL = os.getenv("DATABASE_URL")
# engine = create_engine(DATABASE_URL)
# Session = sessionmaker(bind=engine)
# session = Session()

# # Création des tables (à faire une fois)
# Base.metadata.create_all(engine)

# # Chargement du CSV nettoyé
# df = pd.read_csv('data/jobs_clean.csv')

# df = df.replace({np.nan: None})

# def parse_datetime(dt_str):
#     if pd.isna(dt_str):
#         return None
#     try:
#         return datetime.fromisoformat(dt_str)
#     except Exception:
#         return None

# for idx, row in df.iterrows():
#     # Gérer l'entreprise
#     company = session.query(Company).filter_by(name=row['company_name']).first()
#     if not company:
#         company = Company(
#             name=row['company_name'],
#             industry=row.get('industry'),
#             creation_year=row.get('creation_year'),
#             nb_employees=row.get('nb_employees'),
#             parity_women=row.get('parity_women'),
#             average_age=row.get('average_age'),
#             url=row.get('company_url'),
#             logo=row.get('company_logo'),
#             description=row.get('company_description'),
#             media_website=row.get('media_website'),
#             media_linkedin=row.get('media_linkedin'),
#             media_twitter=row.get('media_twitter'),
#             media_github=row.get('media_github'),
#             media_stackoverflow=row.get('media_stackoverflow'),
#             media_behance=row.get('media_behance'),
#             media_dribbble=row.get('media_dribbble'),
#             media_xing=row.get('media_xing'),
#         )
#         session.add(company)
#         # Pas de commit ici, on attend la fin de la boucle pour faire un seul commit

#     # Création du job
#     job = Job(
#         wttj_reference=row.get('wttj_reference'),
#         job_reference=row.get('job_reference'),
#         poste=row.get('poste'),
#         description=row.get('description'),
#         profile=row.get('profile'),
#         published_at=parse_datetime(row.get('published_at')),
#         updated_at=parse_datetime(row.get('updated_at')),
#         url=row.get('url'),
#         remote=row.get('remote'),
#         remote_policy=row.get('remote_policy'),
#         office_remote_ratio=row.get('office_remote_ratio'),
#         contract_type=row.get('contract_type'),
#         contract_duration_min=row.get('contract_duration_min'),
#         contract_duration_max=row.get('contract_duration_max'),
#         salary_min=row.get('salary_min'),
#         salary_max=row.get('salary_max'),
#         salary_currency=row.get('salary_currency'),
#         salary_period=row.get('salary_period'),
#         education_level=row.get('education_level'),
#         recruitment_process=row.get('recruitment_process'),
#         profession=row.get('profession'),
#         company=company,
#     )

#     # Nettoyer les valeurs NaN dans le job
#     # fix_nan_in_job(job)

#     session.add(job)

#     # Tags
#     tags = str(row.get('tags')).split(',')
#     for t in tags:
#         t = t.strip()
#         if not t:
#             continue
#         tag = session.query(Tag).filter_by(name=t).first()
#         if not tag:
#             tag = Tag(name=t)
#             session.add(tag)
#             # Pas de commit ici
#         if tag not in job.tags:
#             job.tags.append(tag)

#     # Locations
#     locations = str(row.get('locations')).split(',')
#     for loc in locations:
#         loc = loc.strip()
#         if not loc:
#             continue
#         location = session.query(Location).filter_by(name=loc).first()
#         if not location:
#             location = Location(name=loc)
#             session.add(location)
#             # Pas de commit ici
#         if location not in job.locations:
#             job.locations.append(location)

#     # Languages
#     languages = str(row.get('languages')).split(',')
#     for lang in languages:
#         lang = lang.strip()
#         if not lang:
#             continue
#         language = session.query(Language).filter_by(code=lang).first()
#         if not language:
#             language = Language(code=lang)
#             session.add(language)
#             # Pas de commit ici
#         if language not in job.languages:
#             job.languages.append(language)

#     # Commit une fois par job (avec tous les ajouts liés)
#     session.commit()

# session.close()
# print("Insertion terminée !")
import pandas as pd
import numpy as np
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, Company, Job, Location, Media, Skill, Tool, Benefit
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Chargement du CSV
df = pd.read_csv("data/jobs_clean.csv")
df = df.replace({np.nan: None})

def parse_datetime(value):
    try:
        return datetime.fromisoformat(value) if value else None
    except:
        return None

for _, row in df.iterrows():
    # Vérifie ou insère la Company
    company = session.query(Company).filter_by(name=row["company_name"]).first()
    if not company:
        company = Company(
            name=row["company_name"],
            industry=row["industry"],
            creation_year=row["creation_year"],
            nb_employees=row["nb_employees"],
            parity_women=row["parity_women"],
            average_age=row["average_age"],
            url=row["company_url"],
            description=row["company_description"]
        )
        session.add(company)
        session.flush()  # pour générer l'ID

    # Vérifie ou insère la Location
    location_name = row["locations"]
    location = session.query(Location).filter_by(city=location_name).first()
    if not location:
        location = Location(city=location_name)
        session.add(location)
        session.flush()

    # Crée le Job
    job = Job(
        job_reference=row["job_reference"],
        wttj_reference=row["wttj_reference"],
        poste=row["poste"],
        remote=row["remote"],
        url=row["url"],
        education_level=row["education_level"],
        profile=row["profile"],
        salary_min=row["salary_min"],
        salary_max=row["salary_max"],
        salary_currency=row["salary_currency"],
        salary_period=row["salary_period"],
        published_at=parse_datetime(row["published_at"]),
        updated_at=parse_datetime(row["updated_at"]),
        profession=row["profession"],
        contract_type=row["contract_type"],
        contract_duration_min=row["contract_duration_min"],
        contract_duration_max=row["contract_duration_max"],
        recruitment_process=row["recruitment_process"],
        cover_letter=bool(row["cover_letter"]),
        resume=bool(row["resume"]),
        portfolio=bool(row["portfolio"]),
        picture=bool(row["picture"]),
        company_id=company.id,
        location_id=location.id
    )
    session.add(job)
    session.flush()

    # Crée Media (1:1)
    media = Media(
        job_reference=job.job_reference,
        website=row["media_website"],
        linkedin=row["media_linkedin"],
        twitter=row["media_twitter"],
        github=row["media_github"],
        stackoverflow=row["media_stackoverflow"],
        behance=row["media_behance"],
        dribbble=row["media_dribbble"],
        xing=row["media_xing"]
    )
    session.add(media)

    # Crée Skills (1:n)
    skills = str(row.get("skills", "")).split(",")
    for s in skills:
        s = s.strip()
        if s:
            skill = Skill(job_reference=job.job_reference, skill=s)
            session.add(skill)

    # Crée Tools (1:n)
    tools = str(row.get("tags", "")).split(",")
    for t in tools:
        t = t.strip()
        if t:
            tool = Tool(job_reference=job.job_reference, tool=t)
            session.add(tool)

    # Crée Benefits (1:n)
    benefits = str(row.get("benefits", "")).split(",")
    for b in benefits:
        b = b.strip()
        if b:
            benefit = Benefit(job_reference=job.job_reference, benefit=b)
            session.add(benefit)

    session.commit()

session.close()
print("Données insérées avec succès dans Azure SQL Database.")

