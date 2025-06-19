# # from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, Table, DateTime
# # from sqlalchemy.orm import relationship, declarative_base

# # Base = declarative_base()

# # # Table d'association many-to-many
# # job_tags = Table(
# #     'job_tags', Base.metadata,
# #     Column('job_id', Integer, ForeignKey('jobs.id')),
# #     Column('tag_id', Integer, ForeignKey('tags.id'))
# # )

# # job_locations = Table(
# #     'job_locations', Base.metadata,
# #     Column('job_id', Integer, ForeignKey('jobs.id')),
# #     Column('location_id', Integer, ForeignKey('locations.id'))
# # )

# # job_languages = Table(
# #     'job_languages', Base.metadata,
# #     Column('job_id', Integer, ForeignKey('jobs.id')),
# #     Column('language_id', Integer, ForeignKey('languages.id'))
# # )

# # class Company(Base):
# #     __tablename__ = 'companies'
# #     id = Column(Integer, primary_key=True)
# #     name = Column(String(255))
# #     industry = Column(Text, nullable=True)
# #     creation_year = Column(Integer)
# #     nb_employees = Column(Integer)
# #     parity_women = Column(Float)
# #     average_age = Column(Float)
# #     url = Column(String(500))  # URL de l'entreprise
# #     logo = Column(Text)
# #     description = Column(Text)
# #     media_website = Column(String(500))
# #     media_linkedin = Column(String(500))
# #     media_twitter = Column(String(500))
# #     media_github = Column(String(500))
# #     media_stackoverflow = Column(String(500))
# #     media_behance = Column(String(500))
# #     media_dribbble = Column(String(500))
# #     media_xing = Column(String(500))
# #     jobs = relationship("Job", back_populates="company")


# # class Job(Base):
# #     __tablename__ = 'jobs'
# #     id = Column(Integer, primary_key=True)
# #     wttj_reference = Column(String(100))
# #     job_reference = Column(String(100))
# #     poste = Column(String(255))
# #     description = Column(Text)
# #     profile = Column(Text)
# #     published_at = Column(DateTime)
# #     updated_at = Column(DateTime)
# #     url = Column(String(500))
# #     remote = Column(String(50))
# #     remote_policy = Column(String(255))
# #     office_remote_ratio = Column(Float)
# #     contract_type = Column(String(50))
# #     contract_duration_min = Column(Integer)
# #     contract_duration_max = Column(Integer)
# #     salary_min = Column(Float)
# #     salary_max = Column(Float)
# #     salary_currency = Column(String(10))
# #     salary_period = Column(String(50))
# #     education_level = Column(String(100))
# #     recruitment_process = Column(Text)
# #     profession = Column(String(255))


# #     company_id = Column(Integer, ForeignKey('companies.id'))
# #     company = relationship("Company", back_populates="jobs")

# #     tags = relationship("Tag", secondary=job_tags, back_populates="jobs")
# #     locations = relationship("Location", secondary=job_locations, back_populates="jobs")
# #     languages = relationship("Language", secondary=job_languages, back_populates="jobs")


# # class Tag(Base):
# #     __tablename__ = 'tags'
# #     id = Column(Integer, primary_key=True)
# #     name = Column(String)
# #     jobs = relationship("Job", secondary=job_tags, back_populates="tags")


# # class Location(Base):
# #     __tablename__ = 'locations'
# #     id = Column(Integer, primary_key=True)
# #     name = Column(String)
# #     jobs = relationship("Job", secondary=job_locations, back_populates="locations")


# # class Language(Base):
# #     __tablename__ = 'languages'
# #     id = Column(Integer, primary_key=True)
# #     code = Column(String)
# #     jobs = relationship("Job", secondary=job_languages, back_populates="languages")
# from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
# from sqlalchemy.orm import relationship, declarative_base

# Base = declarative_base()


# # ---------- Company ----------
# class Company(Base):
#     __tablename__ = "companies"

#     id = Column(Integer, primary_key=True)
#     company_name = Column(String)
#     industry = Column(String)
#     creation_year = Column(String)
#     parity_women = Column(String)
#     nb_employees = Column(String)
#     average_age = Column(String)
#     company_url = Column(Text)
#     company_description = Column(Text)

#     jobs = relationship("Job", back_populates="company")


# # ---------- Location ----------
# class Location(Base):
#     __tablename__ = "locations"

#     id = Column(Integer, primary_key=True)
#     address = Column(Text)
#     local_address = Column(Text)
#     city = Column(String)
#     zip_code = Column(String)
#     district = Column(String)
#     latitude = Column(String)
#     longitude = Column(String)
#     country_code = Column(String)
#     local_city = Column(String)
#     local_district = Column(String)

#     jobs = relationship("Job", back_populates="location")


# # ---------- Job ----------
# class Job(Base):
#     __tablename__ = "jobs"

#     job_reference = Column(String(255), primary_key=True)  # <-- taille fixée ici
#     wttj_reference = Column(String(255), nullable=True)
#     poste = Column(String(255), nullable=True)
#     remote = Column(String(255), nullable=True)
#     url = Column(String(255), nullable=True)
#     education_level = Column(String(255), nullable=True)
#     profile = Column(String(255), nullable=True)
#     salary_min = Column(String(255), nullable=True)
#     salary_max = Column(String(255), nullable=True)
#     salary_currency = Column(String(255), nullable=True)
#     salary_period = Column(String(255), nullable=True)
#     published_at = Column(DateTime, nullable=True)
#     updated_at = Column(DateTime, nullable=True)
#     profession = Column(String(255), nullable=True)
#     contract_type = Column(String(255), nullable=True)
#     contract_duration_min = Column(String(255), nullable=True)
#     contract_duration_max = Column(String(255), nullable=True)
#     recruitment_process = Column(String(255), nullable=True)
#     cover_letter = Column(Boolean, nullable=True)
#     resume = Column(Boolean, nullable=True)
#     portfolio = Column(Boolean, nullable=True)
#     picture = Column(Boolean, nullable=True)

#     company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
#     location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)

#     company = relationship("Company", back_populates="jobs")
#     location = relationship("Location", back_populates="jobs")

#     media = relationship("Media", back_populates="job", uselist=False)
#     skills = relationship("Skill", back_populates="job")
#     tools = relationship("Tool", back_populates="job")
#     benefits = relationship("Benefit", back_populates="job")



# # ---------- Media ----------
# class Media(Base):
#     __tablename__ = "media"

#     id = Column(Integer, primary_key=True)
#     job_reference = Column(String(255), ForeignKey("jobs.job_reference"))
#     website = Column(Text)
#     linkedin = Column(Text)
#     twitter = Column(Text)
#     github = Column(Text)
#     stackoverflow = Column(Text)
#     behance = Column(Text)
#     dribbble = Column(Text)
#     xing = Column(Text)

#     job = relationship("Job", back_populates="media")


# # ---------- Skill ----------
# class Skill(Base):
#     __tablename__ = "skills"

#     id = Column(Integer, primary_key=True)
#     job_reference = Column(String, ForeignKey("jobs.job_reference"))
#     skill = Column(String)

#     job = relationship("Job", back_populates="skills")


# # ---------- Tool ----------
# class Tool(Base):
#     __tablename__ = "tools"

#     id = Column(Integer, primary_key=True)
#     job_reference = Column(String, ForeignKey("jobs.job_reference"))
#     tool = Column(String)

#     job = relationship("Job", back_populates="tools")


# # ---------- Benefit ----------
# class Benefit(Base):
#     __tablename__ = "benefits"

#     id = Column(Integer, primary_key=True)
#     job_reference = Column(String, ForeignKey("jobs.job_reference"))
#     benefit = Column(String)

#     job = relationship("Job", back_populates="benefits")
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# ---------- Company ----------
class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    industry = Column(String, nullable=True)
    creation_year = Column(Integer, nullable=True)
    parity_women = Column(String, nullable=True)
    nb_employees = Column(Integer, nullable=True)
    average_age = Column(Float, nullable=True)
    url = Column(Text, nullable=True)
    description = Column(Text, nullable=True)

    jobs = relationship("Job", back_populates="company")


# ---------- Location ----------
class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True)
    address = Column(Text, nullable=True)
    local_address = Column(Text, nullable=True)
    city = Column(String, nullable=True)
    zip_code = Column(String, nullable=True)
    district = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    country_code = Column(String(10), nullable=True)
    local_city = Column(String, nullable=True)
    local_district = Column(String, nullable=True)

    jobs = relationship("Job", back_populates="location")


# ---------- Job ----------
class Job(Base):
    __tablename__ = "jobs"

    job_reference = Column(String(255), primary_key=True)
    wttj_reference = Column(String(255), nullable=True)
    poste = Column(String(255), nullable=True)
    remote = Column(String(255), nullable=True)
    url = Column(String(255), nullable=True)
    education_level = Column(String(255), nullable=True)
    profile = Column(Text, nullable=True)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    salary_currency = Column(String(10), nullable=True)
    salary_period = Column(String(50), nullable=True)
    published_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    profession = Column(String(255), nullable=True)
    contract_type = Column(String(255), nullable=True)
    contract_duration_min = Column(String(255), nullable=True)
    contract_duration_max = Column(String(255), nullable=True)
    recruitment_process = Column(Text, nullable=True)
    cover_letter = Column(Boolean, nullable=True)
    resume = Column(Boolean, nullable=True)
    portfolio = Column(Boolean, nullable=True)
    picture = Column(Boolean, nullable=True)

    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)

    company = relationship("Company", back_populates="jobs")
    location = relationship("Location", back_populates="jobs")

    media = relationship("Media", back_populates="job", uselist=False)
    skills = relationship("Skill", back_populates="job", cascade="all, delete-orphan")
    tools = relationship("Tool", back_populates="job", cascade="all, delete-orphan")
    benefits = relationship("Benefit", back_populates="job", cascade="all, delete-orphan")


# ---------- Media ----------
class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True)
    job_reference = Column(String(255), ForeignKey("jobs.job_reference"))
    website = Column(Text, nullable=True)
    linkedin = Column(Text, nullable=True)
    twitter = Column(Text, nullable=True)
    github = Column(Text, nullable=True)
    stackoverflow = Column(Text, nullable=True)
    behance = Column(Text, nullable=True)
    dribbble = Column(Text, nullable=True)
    xing = Column(Text, nullable=True)

    job = relationship("Job", back_populates="media")


# ---------- Skill ----------
class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True)
    job_reference = Column(String(255), ForeignKey("jobs.job_reference"))
    skill = Column(String(255), nullable=False)

    job = relationship("Job", back_populates="skills")


# ---------- Tool ----------
class Tool(Base):
    __tablename__ = "tools"

    id = Column(Integer, primary_key=True)
    job_reference = Column(String(255), ForeignKey("jobs.job_reference"))
    tool = Column(String(255), nullable=False)

    job = relationship("Job", back_populates="tools")


# ---------- Benefit ----------
class Benefit(Base):
    __tablename__ = "benefits"

    id = Column(Integer, primary_key=True)
    job_reference = Column(String(255), ForeignKey("jobs.job_reference"))
    benefit = Column(String(255), nullable=False)

    job = relationship("Job", back_populates="benefits")

