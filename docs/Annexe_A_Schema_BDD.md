# ANNEXE A - Schema de la Base de Donnees

## Projet WTTJ - Modelisation des Donnees

---

## 1. Modele Conceptuel de Donnees (MCD)

```
                                    COMPANY
                                 ┌────────────────┐
                                 │ id (PK)        │
                                 │ name           │
                                 │ industry       │
                                 │ creation_year  │
                                 │ nb_employees   │
                                 │ average_age    │
                                 │ parity_women   │
                                 │ url            │
                                 │ description    │
                                 └───────┬────────┘
                                         │
                                         │ 1,n
                                         │
                                    emploie
                                         │
                                         │ 0,n
                                         │
┌────────────────┐                ┌──────┴─────────┐                ┌────────────────┐
│   LOCATION     │                │      JOB       │                │    MEDIA       │
├────────────────┤                ├────────────────┤                ├────────────────┤
│ id (PK)        │   localise     │ job_ref (PK)   │   possede      │ id (PK)        │
│ address        │◄──────────────►│ wttj_reference │◄──────────────►│ job_reference  │
│ city           │      1,n       │ poste          │      1,1       │ website        │
│ zip_code       │                │ remote         │                │ linkedin       │
│ district       │                │ url            │                │ twitter        │
│ latitude       │                │ education_level│                │ github         │
│ longitude      │                │ salary_min/max │                │ stackoverflow  │
│ country_code   │                │ published_at   │                │ behance        │
│ local_city     │                │ contract_type  │                │ dribbble       │
│ local_district │                │ profession     │                │ xing           │
└────────────────┘                └───────┬────────┘                └────────────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
                    │ 1,n                │ 1,n                │ 1,n
                    │                    │                    │
               contient            requiert              offre
                    │                    │                    │
                    │ 0,n                │ 0,n                │ 0,n
                    │                    │                    │
             ┌──────┴──────┐      ┌──────┴──────┐      ┌──────┴──────┐
             │   SKILL     │      │    TOOL     │      │  BENEFIT    │
             ├─────────────┤      ├─────────────┤      ├─────────────┤
             │ id (PK)     │      │ id (PK)     │      │ id (PK)     │
             │ job_ref(FK) │      │ job_ref(FK) │      │ job_ref(FK) │
             │ skill       │      │ tool        │      │ benefit     │
             └─────────────┘      └─────────────┘      └─────────────┘
```

---

## 2. Modele Logique de Donnees (MLD)

```
COMPANY (id, name, industry, creation_year, parity_women, nb_employees,
         average_age, url, description)

LOCATION (id, address, local_address, city, zip_code, district,
          latitude, longitude, country_code, local_city, local_district)

JOB (job_reference, wttj_reference, poste, remote, url, education_level,
     profile, salary_min, salary_max, salary_currency, salary_period,
     published_at, updated_at, profession, contract_type,
     contract_duration_min, contract_duration_max, recruitment_process,
     cover_letter, resume, portfolio, picture,
     #company_id, #location_id)

MEDIA (id, #job_reference, website, linkedin, twitter, github,
       stackoverflow, behance, dribbble, xing)

SKILL (id, #job_reference, skill)

TOOL (id, #job_reference, tool)

BENEFIT (id, #job_reference, benefit)
```

---

## 3. Modele Physique de Donnees (MPD) - SQL Server

```sql
-- Table COMPANIES
CREATE TABLE companies (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL,
    industry NVARCHAR(255),
    creation_year INT,
    parity_women NVARCHAR(50),
    nb_employees INT,
    average_age FLOAT,
    url NVARCHAR(MAX),
    description NVARCHAR(MAX)
);

-- Table LOCATIONS
CREATE TABLE locations (
    id INT IDENTITY(1,1) PRIMARY KEY,
    address NVARCHAR(MAX),
    local_address NVARCHAR(MAX),
    city NVARCHAR(255),
    zip_code NVARCHAR(20),
    district NVARCHAR(255),
    latitude FLOAT,
    longitude FLOAT,
    country_code NVARCHAR(10),
    local_city NVARCHAR(255),
    local_district NVARCHAR(255)
);

-- Table JOBS
CREATE TABLE jobs (
    job_reference NVARCHAR(255) PRIMARY KEY,
    wttj_reference NVARCHAR(255),
    poste NVARCHAR(255),
    remote NVARCHAR(255),
    url NVARCHAR(255),
    education_level NVARCHAR(255),
    profile NVARCHAR(MAX),
    salary_min INT,
    salary_max INT,
    salary_currency NVARCHAR(10),
    salary_period NVARCHAR(50),
    published_at DATETIME,
    updated_at DATETIME,
    profession NVARCHAR(255),
    contract_type NVARCHAR(255),
    contract_duration_min NVARCHAR(255),
    contract_duration_max NVARCHAR(255),
    recruitment_process NVARCHAR(MAX),
    cover_letter BIT,
    resume BIT,
    portfolio BIT,
    picture BIT,
    company_id INT FOREIGN KEY REFERENCES companies(id),
    location_id INT FOREIGN KEY REFERENCES locations(id)
);

-- Table MEDIA
CREATE TABLE media (
    id INT IDENTITY(1,1) PRIMARY KEY,
    job_reference NVARCHAR(255) FOREIGN KEY REFERENCES jobs(job_reference),
    website NVARCHAR(MAX),
    linkedin NVARCHAR(MAX),
    twitter NVARCHAR(MAX),
    github NVARCHAR(MAX),
    stackoverflow NVARCHAR(MAX),
    behance NVARCHAR(MAX),
    dribbble NVARCHAR(MAX),
    xing NVARCHAR(MAX)
);

-- Table SKILLS
CREATE TABLE skills (
    id INT IDENTITY(1,1) PRIMARY KEY,
    job_reference NVARCHAR(255) FOREIGN KEY REFERENCES jobs(job_reference),
    skill NVARCHAR(255) NOT NULL
);

-- Table TOOLS
CREATE TABLE tools (
    id INT IDENTITY(1,1) PRIMARY KEY,
    job_reference NVARCHAR(255) FOREIGN KEY REFERENCES jobs(job_reference),
    tool NVARCHAR(255) NOT NULL
);

-- Table BENEFITS
CREATE TABLE benefits (
    id INT IDENTITY(1,1) PRIMARY KEY,
    job_reference NVARCHAR(255) FOREIGN KEY REFERENCES jobs(job_reference),
    benefit NVARCHAR(255) NOT NULL
);

-- Index pour optimisation
CREATE INDEX idx_jobs_company ON jobs(company_id);
CREATE INDEX idx_jobs_location ON jobs(location_id);
CREATE INDEX idx_skills_job ON skills(job_reference);
CREATE INDEX idx_tools_job ON tools(job_reference);
CREATE INDEX idx_benefits_job ON benefits(job_reference);
```

---

## 4. Dictionnaire des Donnees

### Table: COMPANIES

| Champ | Type | Contrainte | Description |
|-------|------|------------|-------------|
| id | INT | PK, AUTO | Identifiant unique |
| name | NVARCHAR(255) | NOT NULL | Nom de l'entreprise |
| industry | NVARCHAR(255) | | Secteur d'activite |
| creation_year | INT | | Annee de creation |
| parity_women | NVARCHAR(50) | | Pourcentage de femmes |
| nb_employees | INT | | Nombre d'employes |
| average_age | FLOAT | | Age moyen |
| url | NVARCHAR(MAX) | | Site web |
| description | NVARCHAR(MAX) | | Description |

### Table: JOBS

| Champ | Type | Contrainte | Description |
|-------|------|------------|-------------|
| job_reference | NVARCHAR(255) | PK | Reference unique WTTJ |
| wttj_reference | NVARCHAR(255) | | Reference interne |
| poste | NVARCHAR(255) | | Intitule du poste |
| remote | NVARCHAR(255) | | Politique teletravail |
| url | NVARCHAR(255) | | URL de l'offre |
| education_level | NVARCHAR(255) | | Niveau d'etudes requis |
| salary_min | INT | | Salaire minimum |
| salary_max | INT | | Salaire maximum |
| published_at | DATETIME | | Date de publication |
| contract_type | NVARCHAR(255) | | Type de contrat |
| company_id | INT | FK | Lien vers company |
| location_id | INT | FK | Lien vers location |

### Table: SKILLS

| Champ | Type | Contrainte | Description |
|-------|------|------------|-------------|
| id | INT | PK, AUTO | Identifiant unique |
| job_reference | NVARCHAR(255) | FK | Reference du job |
| skill | NVARCHAR(255) | NOT NULL | Competence requise |

---

## 5. Statistiques de la Base

| Table | Nombre d'enregistrements |
|-------|-------------------------|
| companies | 1 247 |
| locations | 523 |
| jobs | 3 695 |
| media | 3 695 |
| skills | 6 943 |
| tools | 9 307 |
| benefits | 54 375 |

**Total:** ~80 000 enregistrements

---

*Document genere pour le rapport E4 - Certification Expert en Donnees Massives*
