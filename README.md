# WTTJ - Welcome To The Jungle Job Scraper & API

Projet de scraping d'offres d'emploi depuis Welcome To The Jungle avec une API REST pour consulter les donnees.

## Table des matieres

- [Architecture du projet](#architecture-du-projet)
- [Schema de la base de donnees](#schema-de-la-base-de-donnees)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Scripts disponibles](#scripts-disponibles)
- [API Endpoints](#api-endpoints)

---

## Architecture du projet

```
wttj/
├── main_api.py              # Point d'entree de l'API FastAPI
├── main_scraper.py          # Point d'entree du scraper
├── config.py                # Configuration (mots-cles, pays)
├── requirements.txt         # Dependances Python
├── .env                     # Variables d'environnement (non versionne)
│
├── src/
│   ├── api/
│   │   ├── auth.py          # Authentification JWT
│   │   └── routers/
│   │       ├── auth.py      # Route /auth/login
│   │       ├── jobs.py      # Route /jobs (protegee)
│   │       ├── companies.py # Route /companies
│   │       ├── locations.py # Route /locations
│   │       └── skills.py    # Route /skills
│   │
│   ├── database/
│   │   ├── db.py            # Connexion SQLAlchemy
│   │   └── models.py        # Modeles ORM (Company, Job, Location, etc.)
│   │
│   ├── scrapper/
│   │   ├── job_scraper.py   # Scraper Selenium (collecte des liens)
│   │   └── api_scraper.py   # Enrichissement via API WTTJ
│   │
│   ├── schemas/
│   │   └── job.py           # Schemas Pydantic
│   │
│   └── services/
│       ├── data_loader.py   # Chargement des donnees
│       └── data_cleaner.py  # Nettoyage des donnees
│
├── scripts/
│   ├── database/
│   │   ├── create_tables.py    # Cree les tables en base
│   │   ├── reset_database.py   # Supprime et recree les tables
│   │   └── test_connection.py  # Teste la connexion a la base
│   │
│   └── data/
│       ├── insert_data.py      # Insere les donnees du CSV
│       └── insert_clean_data.py # Insere les donnees nettoyees
│
└── data/
    └── data.csv             # Donnees scrapees (genere)
```

---

## Schema de la base de donnees

```
┌─────────────────┐       ┌─────────────────────────────────────────┐
│   companies     │       │                  jobs                   │
├─────────────────┤       ├─────────────────────────────────────────┤
│ id (PK)         │◄──┐   │ job_reference (PK)                      │
│ name            │   │   │ wttj_reference                          │
│ industry        │   │   │ poste                                   │
│ creation_year   │   │   │ remote                                  │
│ parity_women    │   │   │ url                                     │
│ nb_employees    │   │   │ education_level                         │
│ average_age     │   │   │ profile                                 │
│ url             │   │   │ salary_min / salary_max                 │
│ description     │   │   │ salary_currency / salary_period         │
└─────────────────┘   │   │ published_at / updated_at               │
                      │   │ profession                              │
┌─────────────────┐   │   │ contract_type                           │
│   locations     │   │   │ contract_duration_min / max             │
├─────────────────┤   │   │ recruitment_process                     │
│ id (PK)         │◄──┼───│ cover_letter / resume / portfolio       │
│ address         │   │   │ picture                                 │
│ local_address   │   │   │ company_id (FK) ──────────────────────┬─┘
│ city            │   │   │ location_id (FK) ─────────────────────┘
│ zip_code        │   │   └─────────────────────────────────────────┘
│ district        │   │               │
│ latitude        │   └───────────────┤
│ longitude       │                   │
│ country_code    │                   ▼
│ local_city      │   ┌─────────────────────────────────────────┐
│ local_district  │   │              Relations 1:N              │
└─────────────────┘   └─────────────────────────────────────────┘
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
        ▼                             ▼                             ▼
┌───────────────┐           ┌───────────────┐           ┌───────────────┐
│    skills     │           │     tools     │           │   benefits    │
├───────────────┤           ├───────────────┤           ├───────────────┤
│ id (PK)       │           │ id (PK)       │           │ id (PK)       │
│ job_reference │           │ job_reference │           │ job_reference │
│ skill         │           │ tool          │           │ benefit       │
└───────────────┘           └───────────────┘           └───────────────┘

┌───────────────────────────────────────────────────────────────────────┐
│                              media                                    │
├───────────────────────────────────────────────────────────────────────┤
│ id (PK) │ job_reference (FK) │ website │ linkedin │ twitter │ github │
│         │                    │ stackoverflow │ behance │ dribbble    │
└───────────────────────────────────────────────────────────────────────┘
```

---

## Installation

### Prerequis

- Python 3.10+
- Chrome + ChromeDriver (pour le scraping)
- ODBC Driver 18 for SQL Server

### Etapes

```bash
# 1. Cloner le projet
git clone <repo-url>
cd wttj

# 2. Creer un environnement virtuel
python -m venv venv

# 3. Activer l'environnement
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 4. Installer les dependances
pip install -r requirements.txt

# 5. Installer les dependances supplementaires pour l'API
pip install python-jose[cryptography] passlib[bcrypt]
```

---

## Configuration

Creer un fichier `.env` a la racine du projet :

```env
# Base de donnees Azure SQL Server
SQL_SERVER=votre-serveur.database.windows.net
SQL_DATABASE=wttj
SQL_USERNAME=votre-username
SQL_PASSWORD=votre-password

# Azure Storage (optionnel - pour le data lake)
RESOURCE_GROUP=votre-resource-group
LOCATION=francecentral
STORAGE_ACCOUNT=votre-storage-account
CONTAINER_NAME=wttj
ACCOUNT_KEY=votre-account-key
```

### Configuration du scraping

Modifier `config.py` pour personnaliser les mots-cles et le pays :

```python
COUNTRY = "France"
COUNTRY_CODE = "FR"
KEYWORDS = [
    'data analyst', 'data engineer', 'data scientist',
    'machine learning', 'business intelligence', ...
]
```

---

## Utilisation

### 1. Lancer le scraping

Collecte les offres d'emploi depuis Welcome To The Jungle :

```bash
python main_scraper.py
```

Resultat : fichier `data/data.csv` genere avec toutes les offres.

### 2. Creer les tables en base

```bash
python scripts/database/create_tables.py
```

### 3. Inserer les donnees

```bash
python scripts/data/insert_data.py
```

### 4. Lancer l'API

```bash
uvicorn main_api:app --reload --host 127.0.0.1 --port 8000
```

L'API sera accessible sur : http://127.0.0.1:8000

Documentation Swagger : http://127.0.0.1:8000/docs

---

## Scripts disponibles

| Script | Description |
|--------|-------------|
| `main_scraper.py` | Lance le scraping complet (Selenium + API WTTJ) |
| `main_api.py` | Lance l'API FastAPI |
| `scripts/database/create_tables.py` | Cree les tables dans Azure SQL |
| `scripts/database/reset_database.py` | Supprime et recree toutes les tables |
| `scripts/database/test_connection.py` | Teste la connexion a la base |
| `scripts/data/insert_data.py` | Insere les donnees CSV en base |

### Detail des scripts principaux

#### `main_scraper.py`
1. Utilise Selenium pour parcourir les pages de recherche WTTJ
2. Collecte les liens des offres d'emploi
3. Appelle l'API WTTJ pour enrichir chaque offre (details, skills, benefits)
4. Exporte le tout dans `data/data.csv`

#### `main_api.py`
Lance une API REST FastAPI avec :
- Authentification JWT
- Routes pour consulter jobs, companies, locations, skills
- Pagination sur toutes les routes

---

## API Endpoints

### Authentification

```bash
# Obtenir un token
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin123

# Response
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### Routes disponibles

| Methode | Endpoint | Auth | Description |
|---------|----------|------|-------------|
| GET | `/` | Non | Message de bienvenue |
| GET | `/health` | Non | Status de l'API |
| POST | `/auth/login` | Non | Authentification |
| GET | `/jobs/` | Oui | Liste des offres (paginee) |
| GET | `/companies/` | Non | Liste des entreprises |
| GET | `/locations/` | Non | Liste des localisations |
| GET | `/skills/` | Non | Liste des competences |

### Parametres de pagination

Toutes les routes de liste acceptent :
- `skip` : nombre d'elements a ignorer (defaut: 0)
- `limit` : nombre max d'elements (defaut: 10, max: 100)

### Exemple d'appel

```bash
# Avec curl
curl -X GET "http://127.0.0.1:8000/jobs/?skip=0&limit=10" \
  -H "Authorization: Bearer <votre-token>"

# Liste des entreprises (sans auth)
curl -X GET "http://127.0.0.1:8000/companies/?limit=5"
```

---

## Workflow complet

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  main_scraper.py │────▶│    data.csv      │────▶│  insert_data.py  │
│   (Selenium +    │     │  (fichier local) │     │  (vers Azure SQL)│
│    API WTTJ)     │     │                  │     │                  │
└──────────────────┘     └──────────────────┘     └──────────────────┘
                                                           │
                                                           ▼
                         ┌──────────────────┐     ┌──────────────────┐
                         │  Utilisateurs    │◀────│   main_api.py    │
                         │  (via API REST)  │     │    (FastAPI)     │
                         └──────────────────┘     └──────────────────┘
```

---

## Technologies utilisees

- **Scraping** : Selenium, BeautifulSoup, Requests
- **API** : FastAPI, Uvicorn
- **Base de donnees** : Azure SQL Server, SQLAlchemy
- **Authentification** : JWT (python-jose), Passlib
- **Data** : Pandas, NumPy
