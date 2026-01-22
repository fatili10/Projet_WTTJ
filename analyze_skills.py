from src.database.db import engine
from src.database.models import Skill, Job
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

Session = sessionmaker(bind=engine)
session = Session()

# Compter le nombre de skills par job
skills_per_job = session.query(
    Skill.job_reference,
    func.count(Skill.id).label('skill_count')
).group_by(Skill.job_reference).all()

# Statistiques
skill_counts = [count for _, count in skills_per_job]

print(f"Total de jobs avec skills: {len(skills_per_job)}")
print(f"Jobs avec 1 skill: {sum(1 for c in skill_counts if c == 1)}")
print(f"Jobs avec 2 skills: {sum(1 for c in skill_counts if c == 2)}")
print(f"Jobs avec 3+ skills: {sum(1 for c in skill_counts if c >= 3)}")
print(f"Max skills pour un job: {max(skill_counts)}")

# Trouver un job avec beaucoup de skills
job_ref_with_many = [ref for ref, count in skills_per_job if count >= 5][0]
job = session.query(Job).filter_by(job_reference=job_ref_with_many).first()
skills = session.query(Skill).filter_by(job_reference=job_ref_with_many).all()

print(f"\nExemple d'un job avec {len(skills)} skills:")
print(f"Job: {job.poste}")
for skill in skills[:10]:
    print(f"  - {skill.skill}")

session.close()
