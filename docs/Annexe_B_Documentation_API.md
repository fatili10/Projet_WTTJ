# ANNEXE B - Documentation de l'API REST

## Projet WTTJ - API de Mise a Disposition des Donnees

---

## 1. Informations Generales

| Propriete | Valeur |
|-----------|--------|
| **Titre** | WTTJ Jobs API |
| **Version** | 1.0.0 |
| **Base URL** | `http://127.0.0.1:8000` |
| **Documentation** | `/docs` (Swagger UI) |
| **Schema OpenAPI** | `/openapi.json` |

---

## 2. Authentification

L'API utilise l'authentification **JWT (JSON Web Token)** pour securiser certains endpoints.

### 2.1 Obtenir un Token

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin123
```

**Reponse:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2.2 Utiliser le Token

Ajouter le header `Authorization` a chaque requete protegee:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 2.3 Duree de Validite

- **Expiration:** 60 minutes
- **Algorithme:** HS256

---

## 3. Endpoints

### 3.1 Health Check

```http
GET /
```

**Reponse:**
```json
{
  "message": "Bienvenue sur l'API WTTJ"
}
```

---

```http
GET /health
```

**Reponse:**
```json
{
  "status": "ok",
  "message": "API is running",
  "database": "connected"
}
```

---

### 3.2 Jobs (Protege)

```http
GET /jobs/
Authorization: Bearer {token}
```

**Parametres de requete:**

| Parametre | Type | Defaut | Description |
|-----------|------|--------|-------------|
| skip | int | 0 | Nombre d'elements a ignorer |
| limit | int | 10 | Nombre max d'elements (max: 100) |

**Exemple de reponse:**
```json
[
  {
    "job_reference": "ACME_abc123",
    "wttj_reference": "wttj_xyz789",
    "poste": "Data Engineer",
    "remote": "partial",
    "url": "https://www.welcometothejungle.com/...",
    "education_level": "bac_5",
    "profile": "Nous recherchons un Data Engineer...",
    "salary_min": 45000,
    "salary_max": 55000,
    "salary_currency": "EUR",
    "salary_period": "yearly",
    "published_at": "2026-01-15T10:30:00",
    "updated_at": "2026-01-18T14:00:00",
    "profession": "Data",
    "contract_type": "CDI",
    "company": {
      "id": 42,
      "name": "ACME Corp",
      "industry": "Tech",
      "creation_year": 2015,
      "nb_employees": 150,
      "average_age": 32.5,
      "url": "https://acme.com"
    },
    "location": {
      "id": 15,
      "city": "Paris",
      "address": "10 rue de la Data",
      "zip_code": "75001",
      "country_code": "FR",
      "latitude": 48.8566,
      "longitude": 2.3522
    },
    "skills": ["Python", "SQL", "Spark", "Airflow"],
    "tools": ["Docker", "Kubernetes", "AWS"],
    "benefits": ["Teletravail", "RTT", "Tickets restaurant"],
    "media": {
      "website": "https://acme.com",
      "linkedin": "https://linkedin.com/company/acme",
      "github": "https://github.com/acme"
    }
  }
]
```

---

### 3.3 Companies

```http
GET /companies/
```

**Parametres de requete:**

| Parametre | Type | Defaut | Description |
|-----------|------|--------|-------------|
| skip | int | 0 | Nombre d'elements a ignorer |
| limit | int | 10 | Nombre max d'elements (max: 100) |

**Exemple de reponse:**
```json
[
  {
    "id": 1,
    "name": "ACME Corp",
    "industry": "Tech",
    "creation_year": 2015,
    "parity_women": "45%",
    "nb_employees": 150,
    "average_age": 32.5,
    "url": "https://acme.com",
    "description": "Leader de la data en France..."
  }
]
```

---

### 3.4 Locations

```http
GET /locations/
```

**Exemple de reponse:**
```json
[
  {
    "id": 1,
    "address": "10 rue de la Data",
    "local_address": null,
    "city": "Paris",
    "zip_code": "75001",
    "district": "1er",
    "latitude": 48.8566,
    "longitude": 2.3522,
    "country_code": "FR",
    "local_city": "Paris",
    "local_district": "Louvre"
  }
]
```

---

### 3.5 Skills

```http
GET /skills/
```

**Exemple de reponse:**
```json
[
  {
    "id": 1,
    "skill": "Python",
    "job_reference": "ACME_abc123"
  },
  {
    "id": 2,
    "skill": "SQL",
    "job_reference": "ACME_abc123"
  }
]
```

---

### 3.6 Tools

```http
GET /tools/
```

**Exemple de reponse:**
```json
[
  {
    "id": 1,
    "tool": "Docker",
    "job_reference": "ACME_abc123"
  }
]
```

---

### 3.7 Benefits

```http
GET /benefits/
```

**Exemple de reponse:**
```json
[
  {
    "id": 1,
    "benefit": "Teletravail",
    "job_reference": "ACME_abc123"
  }
]
```

---

### 3.8 Media

```http
GET /media/
```

**Exemple de reponse:**
```json
[
  {
    "id": 1,
    "job_reference": "ACME_abc123",
    "website": "https://acme.com",
    "linkedin": "https://linkedin.com/company/acme",
    "twitter": null,
    "github": "https://github.com/acme",
    "stackoverflow": null,
    "behance": null,
    "dribbble": null,
    "xing": null
  }
]
```

---

## 4. Codes d'Erreur

| Code | Signification |
|------|---------------|
| 200 | Succes |
| 401 | Non authentifie (token manquant/invalide) |
| 403 | Acces refuse |
| 404 | Ressource non trouvee |
| 422 | Erreur de validation |
| 500 | Erreur serveur |

**Exemple d'erreur 401:**
```json
{
  "detail": "Token invalide ou expire"
}
```

---

## 5. Exemples avec cURL

### Obtenir un token
```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

### Lister les jobs
```bash
curl -X GET "http://127.0.0.1:8000/jobs/?skip=0&limit=5" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Lister les entreprises
```bash
curl -X GET "http://127.0.0.1:8000/companies/?limit=10"
```

---

## 6. Exemples avec Python

```python
import requests

BASE_URL = "http://127.0.0.1:8000"

# 1. Authentification
response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "admin", "password": "admin123"}
)
token = response.json()["access_token"]

# 2. Appel API protege
headers = {"Authorization": f"Bearer {token}"}
jobs = requests.get(
    f"{BASE_URL}/jobs/",
    headers=headers,
    params={"limit": 100}
).json()

print(f"Nombre de jobs: {len(jobs)}")
for job in jobs[:5]:
    print(f"- {job['poste']} @ {job['company']['name']}")
```

---

## 7. Rate Limiting

Actuellement, l'API n'impose pas de rate limiting. En production, il est recommande d'implementer:
- 100 requetes/minute pour les endpoints publics
- 1000 requetes/minute pour les utilisateurs authentifies

---

*Documentation generee pour le rapport E4 - Certification Expert en Donnees Massives*
