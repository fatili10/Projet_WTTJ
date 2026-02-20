# WTTJ - Welcome To The Jungle Job Scraper & API

Projet de scraping d'offres d'emploi depuis Welcome To The Jungle avec un pipeline de données complet : collecte, nettoyage, stockage sur Azure Data Lake Gen2, insertion en base SQL et exposition via une API REST.

## Table des matieres

- [Architecture du projet](#architecture-du-projet)
- [Workflow complet](#workflow-complet)
- [Schema de la base de donnees](#schema-de-la-base-de-donnees)
- [Infrastructure Azure (Terraform)](#infrastructure-azure-terraform)
- [Data Catalog (OpenMetadata)](#data-catalog-openmetadata)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Scripts disponibles](#scripts-disponibles)
- [API Endpoints](#api-endpoints)
- [Technologies utilisees](#technologies-utilisees)

---

## Architecture du projet

```
wttj/
├── main_api.py              # Point d'entree de l'API FastAPI
├── main_scraper.py          # Point d'entree du scraper
├── run_pipeline.py          # Orchestrateur du pipeline complet
├── config.py                # Configuration (mots-cles, pays)
├── requirements.txt         # Dependances Python
├── docker-compose.yml       # Stack OpenMetadata (data catalog)
├── .env                     # Variables d'environnement (non versionne)
│
├── fatima-transfer/
│   └── terraform/           # Infrastructure as Code (Azure)
│       ├── main.tf          # Provider et resource group
│       ├── storage.tf       # ADLS Gen2 + Blob Storage
│       ├── sql.tf           # Azure SQL Server et base de donnees
│       ├── variables.tf     # Declaration des variables
│       ├── outputs.tf       # Sorties (URLs, noms des ressources)
│       └── terraform.tfvars.example  # Exemple de configuration
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
│       ├── insert_data.py          # Insere les donnees du CSV
│       ├── insert_clean_data.py    # Insere les donnees nettoyees
│       └── upload_to_datalake.py   # Upload vers Azure Data Lake Gen2
│
└── data/
    └── archive/             # Archives horodatees des CSV (genere)
```

---

## Workflow complet

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────────┐
│  main_scraper.py │────▶│   data/data.csv  │────▶│  Azure ADLS Gen2     │
│  (Selenium +     │     │  (zone RAW)      │     │  raw/YYYY-MM-DD/     │
│   API WTTJ)      │     └──────────────────┘     └──────────────────────┘
└──────────────────┘              │
                                  ▼
                       ┌──────────────────┐     ┌──────────────────────┐
                       │  data_cleaner.py │────▶│  Azure ADLS Gen2     │
                       │  (nettoyage)     │     │  curated/YYYY-MM-DD/ │
                       └──────────────────┘     └──────────────────────┘
                                  │
                                  ▼
                       ┌──────────────────┐     ┌──────────────────────┐
                       │insert_clean_data │────▶│  Azure SQL Server    │
                       │  (zone SERVING)  │     │  (base wttj)         │
                       └──────────────────┘     └──────────────────────┘
                                                           │
                       ┌──────────────────┐               ▼
                       │  Utilisateurs    │◀────  main_api.py (FastAPI)
                       │  (via API REST)  │
                       └──────────────────┘
```

Le pipeline est orchestre par `run_pipeline.py` qui execute chaque etape sequentiellement et gere les logs et l'archivage.

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
│ local_address   │   │   │ company_id (FK)                        │
│ city            │   │   │ location_id (FK)                       │
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

## Infrastructure Azure (Terraform)

La configuration Terraform dans `fatima-transfer/terraform/` provisionne automatiquement :

- **Azure Data Lake Gen2** (ADLS) — stockage zones RAW et CURATED
- **Azure Blob Storage** — stockage complementaire
- **Azure SQL Server + Database** — zone SERVING (base `wttj`)

### Deployer l'infrastructure

```bash
cd fatima-transfer/terraform

# 1. Copier et remplir le fichier de variables
cp terraform.tfvars.example terraform.tfvars
# Editer terraform.tfvars avec tes valeurs (mots de passe, noms uniques, etc.)

# 2. Initialiser Terraform
terraform init

# 3. Verifier le plan de deploiement
terraform plan

# 4. Appliquer
terraform apply
```

> **Important** : Ne jamais commiter `terraform.tfvars` (contient les secrets) ni `terraform.tfstate`.

---

## Data Catalog (OpenMetadata)

Le fichier `docker-compose.yml` lance une instance locale d'**OpenMetadata** pour cataloguer les donnees du projet.

### Lancer OpenMetadata

```bash
docker compose up -d
```

Services demarres :
- **OpenMetadata UI** : http://localhost:8585
- **Airflow** (ingestion) : http://localhost:8080
- **Elasticsearch** : http://localhost:9200
- MySQL (interne, port 3306)

---

## Installation

### Prerequis

- Python 3.10+
- Chrome + ChromeDriver (pour le scraping)
- ODBC Driver 18 for SQL Server
- Docker (pour OpenMetadata)
- Terraform (pour le provisionnement Azure)

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

# Azure Data Lake Gen2 (ADLS)
STORAGE_ACCOUNT=adlswttjstudent
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

### Pipeline complet (recommande)

```bash
# Execution complete : scraping + upload ADLS + nettoyage + insertion SQL
python run_pipeline.py

# Nettoyage + insertion seulement (si data.csv existe deja)
python run_pipeline.py --clean

# Insertion seulement (si jobs_clean.csv existe deja)
python run_pipeline.py --insert

# Sans archivage des CSV en fin de pipeline
python run_pipeline.py --no-cleanup
```

### Etapes manuelles

```bash
# 1. Scraping
python main_scraper.py

# 2. Creer les tables en base
python scripts/database/create_tables.py

# 3. Inserer les donnees nettoyees
python scripts/data/insert_clean_data.py

# 4. Upload vers le data lake
python scripts/data/upload_to_datalake.py --zone raw --file data/data.csv
python scripts/data/upload_to_datalake.py --zone curated --file data/jobs_clean.csv
python scripts/data/upload_to_datalake.py --zone all

# 5. Lancer l'API
uvicorn main_api:app --reload --host 127.0.0.1 --port 8000
```

L'API sera accessible sur : http://127.0.0.1:8000
Documentation Swagger : http://127.0.0.1:8000/docs

---

## Scripts disponibles

| Script | Description |
|--------|-------------|
| `run_pipeline.py` | Orchestrateur complet du pipeline |
| `main_scraper.py` | Lance le scraping (Selenium + API WTTJ) |
| `main_api.py` | Lance l'API FastAPI |
| `scripts/database/create_tables.py` | Cree les tables dans Azure SQL |
| `scripts/database/reset_database.py` | Supprime et recree toutes les tables |
| `scripts/database/test_connection.py` | Teste la connexion a la base |
| `scripts/data/insert_data.py` | Insere les donnees CSV brutes en base |
| `scripts/data/insert_clean_data.py` | Insere les donnees nettoyees en base |
| `scripts/data/upload_to_datalake.py` | Upload CSV vers Azure ADLS Gen2 |

---

## API Endpoints

### Authentification

```bash
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
curl -X GET "http://127.0.0.1:8000/jobs/?skip=0&limit=10" \
  -H "Authorization: Bearer <votre-token>"

curl -X GET "http://127.0.0.1:8000/companies/?limit=5"
```

---

## Technologies utilisees

- **Scraping** : Selenium, BeautifulSoup, Requests
- **Pipeline** : Python (run_pipeline.py)
- **API** : FastAPI, Uvicorn
- **Base de donnees** : Azure SQL Server, SQLAlchemy
- **Data Lake** : Azure Data Lake Gen2 (ADLS), azure-storage-blob
- **Infrastructure** : Terraform (Azure provider)
- **Data Catalog** : OpenMetadata (Docker)
- **Authentification** : JWT (python-jose), Passlib
- **Data** : Pandas, NumPy
