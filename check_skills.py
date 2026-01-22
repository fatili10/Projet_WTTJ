from src.database.db import engine
from src.database.models import Skill, Job
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()

# Prendre le premier job
job = session.query(Job).first()
print(f'Job: {job.job_reference} - {job.poste}')

# Compter ses skills
skills = session.query(Skill).filter_by(job_reference=job.job_reference).all()
print(f'Nombre de skills pour ce job: {len(skills)}')

for skill in skills:
    print(f'  - {skill.skill}')

print("\n--- Quelques statistiques ---")
# Stats globales
total_jobs = session.query(Job).count()
total_skills = session.query(Skill).count()
print(f'Total jobs: {total_jobs}')
print(f'Total skills: {total_skills}')
print(f'Moyenne skills par job: {total_skills/total_jobs:.2f}')

session.close()
