# RAPPORT E4 - Realisation d'un Service Numerique

## Projet WTTJ - Plateforme de Collecte et Mise a Disposition des Offres d'Emploi Data

---

**Candidat(e):** [Votre Nom]
**Formation:** Expert en Donnees Massives (RNCP 37638)
**Date:** Janvier 2026

---

## Table des matieres

1. [Presentation du projet et contexte](#1-presentation-du-projet-et-contexte)
2. [Specifications techniques](#2-specifications-techniques)
3. [Extraction automatisee des donnees (C8)](#3-extraction-automatisee-des-donnees-c8)
4. [Requetes SQL d'extraction (C9)](#4-requetes-sql-dextraction-c9)
5. [Agregation et nettoyage des donnees (C10)](#5-agregation-et-nettoyage-des-donnees-c10)
6. [Creation de la base de donnees (C11)](#6-creation-de-la-base-de-donnees-c11)
7. [API REST et mise a disposition (C12)](#7-api-rest-et-mise-a-disposition-c12)
8. [Conformite RGPD et vigilances](#8-conformite-rgpd-et-vigilances)
9. [Conclusion et perspectives](#9-conclusion-et-perspectives)

---

## 1. Presentation du projet et contexte

### 1.1 Contexte organisationnel

Le projet WTTJ (Welcome To The Jungle) s'inscrit dans le cadre d'une mission de veille et d'analyse du marche de l'emploi dans le secteur de la Data en France. L'objectif est de fournir aux equipes RH et aux analystes metier un acces structure aux offres d'emploi du domaine Data (Data Analyst, Data Engineer, Data Scientist, etc.).

### 1.2 Expression du besoin

**Problematique:** Les donnees d'offres d'emploi sont dispersees sur differentes plateformes et ne sont pas exploitables directement pour des analyses statistiques ou du reporting.

**Objectifs fonctionnels:**
- Collecter automatiquement les offres d'emploi Data depuis Welcome To The Jungle
- Structurer et nettoyer les donnees collectees
- Stocker les donnees dans une base relationnelle
- Exposer les donnees via une API REST securisee

**Objectifs techniques:**
- Automatiser l'extraction via scraping et appels API
- Implementer une base de donnees relationnelle sur Azure SQL Server
- Developper une API REST avec authentification JWT
- Assurer la conformite RGPD

### 1.3 Environnement technique

| Composant | Technologie |
|-----------|-------------|
| Scraping | Selenium, BeautifulSoup |
| Langage | Python 3.12 |
| Base de donnees | Azure SQL Server |
| ORM | SQLAlchemy |
| API | FastAPI, Uvicorn |
| Authentification | JWT (python-jose) |
| Versioning | Git |

### 1.4 Organisation du projet

Le projet a ete realise en methodologie Agile avec les phases suivantes:
- **Sprint 1:** Developpement des scripts de scraping
- **Sprint 2:** Conception et creation de la base de donnees
- **Sprint 3:** Developpement de l'API REST
- **Sprint 4:** Tests, documentation et mise en production

---

## 2. Specifications techniques

### 2.1 Architecture globale

Le systeme est compose de trois modules principaux:

```
[Sources Web]          [Traitement]           [Stockage]         [Exposition]
     |                      |                      |                   |
  WTTJ.com  ------>  Scraper + API  ------>  Azure SQL  ------>  API REST
     |              Enrichissement           Server              FastAPI
     |                      |                      |                   |
   HTML/JSON           Python/Pandas         SQLAlchemy          JWT Auth
```

### 2.2 Sources de donnees

L'extraction combine deux sources:
1. **Scraping web (Selenium):** Collecte des liens d'offres depuis les pages de recherche
2. **API WTTJ:** Enrichissement des donnees via l'API interne de Welcome To The Jungle

### 2.3 Volumetrie

| Metrique | Valeur |
|----------|--------|
| Offres collectees | 3 695 jobs uniques |
| Entreprises | 1 200+ |
| Localisations | 500+ |
| Skills | 6 943 |
| Tools | 9 307 |
| Benefits | 54 375 |

---

## 3. Extraction automatisee des donnees (C8)

### 3.1 Script de scraping (`job_scraper.py`)

Le script utilise Selenium en mode headless pour parcourir les pages de recherche:

```python
def _chrome_options():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument(f"user-agent={UserAgent().random}")
    return options

def get_all_data(keyword, country, country_code):
    driver = webdriver.Chrome(options=_chrome_options())
    page = 1
    rows = []

    while True:
        url = f"https://www.welcometothejungle.com/en/jobs?..."
        driver.get(url)
        jobs = driver.find_elements(By.CSS_SELECTOR,
            '[data-testid="search-results-list-item-wrapper"]')

        if not jobs:
            break

        for job in jobs:
            link = job.find_element(By.CSS_SELECTOR,
                'a[href^="/en/companies"]').get_attribute("href")
            rows.append({"link": link, ...})
        page += 1

    driver.quit()
    return pd.DataFrame(rows)
```

**Points cles:**
- Rotation des User-Agents pour eviter le blocage
- Pagination automatique jusqu'a epuisement des resultats
- Gestion des exceptions pour robustesse

### 3.2 Enrichissement via API (`api_scraper.py`)

Chaque lien collecte est enrichi via l'API interne de WTTJ:

```python
def _api_url(job_url):
    part = re.findall(".+/companies(.+)", job_url)[0]
    return "https://api.welcometothejungle.com/api/v1/organizations" + part

def enrich_dataset(df_links):
    rows = []
    for link in tqdm(df_links["link"]):
        data = requests.get(_api_url(link)).json()
        job = data["job"]
        rows.append({
            "job_reference": job["reference"],
            "poste": job["name"],
            "skills": ", ".join(s["name"]["fr"] for s in job.get("skills", [])),
            "tools": ", ".join(t["name"] for t in job.get("tools", [])),
            # ... autres champs
        })
    return pd.DataFrame(rows)
```

### 3.3 Configuration des mots-cles (`config.py`)

```python
COUNTRY = "France"
COUNTRY_CODE = "FR"
KEYWORDS = [
    'data analyst', 'data engineer', 'data scientist',
    'machine learning', 'business intelligence',
    'data architect', 'intelligence artificielle'
]
```

**Depot Git:** Le script est versionne et accessible sur le depot du projet.

---

## 4. Requetes SQL d'extraction (C9)

### 4.1 Requetes d'extraction avec SQLAlchemy

Les requetes utilisent l'ORM SQLAlchemy pour l'extraction des donnees:

```python
# Extraction des jobs avec jointures
jobs = (
    db.query(Job)
    .options(
        joinedload(Job.company),
        joinedload(Job.location),
        joinedload(Job.skills),
        joinedload(Job.tools)
    )
    .order_by(Job.job_reference)
    .offset(skip)
    .limit(limit)
    .all()
)
```

### 4.2 Requetes SQL equivalentes

```sql
-- Extraction des offres avec entreprise et localisation
SELECT j.*, c.name as company_name, l.city
FROM jobs j
LEFT JOIN companies c ON j.company_id = c.id
LEFT JOIN locations l ON j.location_id = l.id
ORDER BY j.job_reference
OFFSET 0 ROWS FETCH NEXT 100 ROWS ONLY;

-- Agregation des skills par job
SELECT j.job_reference, STRING_AGG(s.skill, ', ') as skills
FROM jobs j
JOIN skills s ON j.job_reference = s.job_reference
GROUP BY j.job_reference;

-- Statistiques par type de contrat
SELECT contract_type, COUNT(*) as nb_offres,
       AVG(salary_min) as salaire_moyen_min
FROM jobs
WHERE salary_min IS NOT NULL
GROUP BY contract_type
ORDER BY nb_offres DESC;
```

### 4.3 Optimisations

- Utilisation de `joinedload` pour eviter le probleme N+1
- Index sur `job_reference` (cle primaire)
- Pagination obligatoire avec `ORDER BY` pour MSSQL

---

## 5. Agregation et nettoyage des donnees (C10)

### 5.1 Pipeline d'agregation

Le script `insert_clean_data.py` realise l'agregation:

```python
def safe_get(row, key):
    """Gestion des valeurs nulles"""
    value = row.get(key)
    return None if pd.isna(value) else value

def parse_datetime(dt_str):
    """Conversion des dates"""
    if pd.isna(dt_str):
        return None
    return pd.to_datetime(dt_str)

def parse_bool(value):
    """Normalisation des booleens"""
    if pd.isna(value):
        return None
    return str(value).lower() in ['true', 'mandatory', 'optional']
```

### 5.2 Regles de nettoyage

| Champ | Traitement |
|-------|------------|
| `skills` | Split par virgule, trim des espaces |
| `salary_min/max` | Conversion en entier, gestion des nulls |
| `published_at` | Parsing ISO 8601 |
| `cover_letter` | Normalisation booleen |
| Doublons | Deduplication sur `job_reference` |

### 5.3 Gestion des doublons

```python
# Verification avant insertion
existing_jobs = set(
    r[0] for r in session.query(Job.job_reference).all()
)

for idx, row in df.iterrows():
    job_ref = safe_get(row, 'job_reference')
    if job_ref in existing_jobs:
        continue  # Skip si deja existant
```

---

## 6. Creation de la base de donnees (C11)

### 6.1 Modele Conceptuel de Donnees (MCD)

*Voir Annexe A - Schema MCD*

Les entites principales:
- **COMPANY** (1,n) --- emploie --- (0,n) **JOB**
- **LOCATION** (1,n) --- localise --- (0,n) **JOB**
- **JOB** (1,1) --- possede --- (0,n) **SKILL**
- **JOB** (1,1) --- utilise --- (0,n) **TOOL**
- **JOB** (1,1) --- offre --- (0,n) **BENEFIT**

### 6.2 Modele Physique de Donnees (MPD)

```python
# models.py - Extrait
class Job(Base):
    __tablename__ = "jobs"

    job_reference = Column(String(255), primary_key=True)
    wttj_reference = Column(String(255))
    poste = Column(String(255))
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    published_at = Column(DateTime)

    company_id = Column(Integer, ForeignKey("companies.id"))
    location_id = Column(Integer, ForeignKey("locations.id"))

    company = relationship("Company", back_populates="jobs")
    skills = relationship("Skill", back_populates="job",
                         cascade="all, delete-orphan")
```

### 6.3 Script de creation des tables

```python
# create_tables.py
from src.database.db import engine
from src.database.models import Base

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Tables creees avec succes!")
```

### 6.4 Configuration Azure SQL Server

```python
# db.py
DATABASE_URL = (
    f"mssql+pyodbc://{username}:{password}@{server}:1433/"
    f"{database}?driver=ODBC+Driver+18+for+SQL+Server"
    f"&Encrypt=yes&TrustServerCertificate=no&Connection+Timeout=30"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
```

---

## 7. API REST et mise a disposition (C12)

### 7.1 Architecture de l'API

L'API est construite avec FastAPI et expose les endpoints suivants:

| Methode | Endpoint | Auth | Description |
|---------|----------|------|-------------|
| GET | `/` | Non | Message de bienvenue |
| GET | `/health` | Non | Status de l'API |
| POST | `/auth/login` | Non | Authentification JWT |
| GET | `/jobs/` | **Oui** | Liste des offres |
| GET | `/companies/` | Non | Liste des entreprises |
| GET | `/locations/` | Non | Liste des localisations |
| GET | `/skills/` | Non | Liste des competences |
| GET | `/tools/` | Non | Liste des outils |
| GET | `/benefits/` | Non | Liste des avantages |

### 7.2 Authentification JWT

```python
# auth.py
SECRET_KEY = "SUPER_SECRET_KEY"  # En production: variable d'env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload.get("sub")
```

### 7.3 Exemple d'endpoint protege

```python
@router.get("/")
def get_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)  # Protection
):
    jobs = db.query(Job).options(...).offset(skip).limit(limit).all()
    return [format_job(job) for job in jobs]
```

### 7.4 Documentation OpenAPI

L'API genere automatiquement une documentation Swagger accessible sur `/docs`:

- Schemas de requetes et reponses
- Authentification OAuth2
- Exemples d'appels

### 7.5 Demonstration avec curl

```bash
# 1. Obtenir un token
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -d "username=admin&password=admin123"

# Response: {"access_token": "eyJ...", "token_type": "bearer"}

# 2. Appeler l'endpoint protege
curl -X GET "http://127.0.0.1:8000/jobs/?limit=5" \
  -H "Authorization: Bearer eyJ..."
```

---

## 8. Conformite RGPD et vigilances

### 8.1 Analyse des donnees personnelles

| Donnee | Classification | Traitement |
|--------|---------------|------------|
| Nom entreprise | Non personnel | Stockage direct |
| Adresse | Potentiellement personnel | Stockage limite |
| Coordonnees GPS | Non personnel | Stockage direct |
| URL offre | Non personnel | Stockage direct |

**Conclusion:** Les donnees collectees sont principalement des donnees d'entreprises et d'offres d'emploi publiques. Aucune donnee personnelle de candidats n'est collectee.

### 8.2 Registre des traitements

| Traitement | Finalite | Base legale | Duree |
|------------|----------|-------------|-------|
| Collecte offres | Analyse marche emploi | Interet legitime | 1 an |
| Stockage BDD | Mise a disposition | Interet legitime | 1 an |
| Acces API | Consultation | Interet legitime | Session |

### 8.3 Mesures de securite

- **Authentification:** JWT avec expiration 1h
- **Chiffrement:** HTTPS/TLS pour l'API
- **Acces BDD:** Connexion chiffree Azure SQL
- **Secrets:** Variables d'environnement (`.env` non versionne)

### 8.4 Difficultes rencontrees

1. **Blocage anti-scraping:** Resolu par rotation User-Agent
2. **Timeout connexion Azure:** Resolu par parametrage timeout
3. **Doublons dans les donnees:** Resolu par deduplication sur cle primaire

---

## 9. Conclusion et perspectives

### 9.1 Bilan technique

Le projet WTTJ a permis de mettre en oeuvre l'ensemble des competences du bloc 2:

| Competence | Realisation |
|------------|-------------|
| C8 - Extraction automatisee | Scraping Selenium + API REST |
| C9 - Requetes SQL | SQLAlchemy ORM + requetes natives |
| C10 - Agregation | Pipeline pandas + nettoyage |
| C11 - Base de donnees | Azure SQL Server + modeles MERISE |
| C12 - API REST | FastAPI + JWT + OpenAPI |

### 9.2 Apprentissages

- Maitrise du scraping web avec Selenium
- Conception de bases de donnees relationnelles
- Developpement d'API REST securisees
- Gestion de projet en methodologie Agile

### 9.3 Ameliorations envisagees

1. **Planification automatique:** Cron job pour scraping quotidien
2. **Cache Redis:** Amelioration des performances API
3. **Dashboard:** Interface de visualisation des donnees
4. **ML:** Modele de recommandation d'offres

---

## Annexes

### Annexe A - Schema de la base de donnees

*Voir fichier: `docs/schema_bdd.png`*

### Annexe B - Documentation API (OpenAPI)

*Accessible sur: `http://127.0.0.1:8000/docs`*

### Annexe C - Depot Git

*URL du depot: [A completer]*

---

**Fin du rapport**
