# import pandas as pd
# import re
# from tqdm import tqdm
# from .utils import fetch_data

# def get_api_url(link_job):
#     part = re.findall('.+/companies(.+)', link_job)[0]
#     return "https://api.welcometothejungle.com/api/v1/organizations" + part

# def get_benefits(data):
#     benefits = data.get('job', {}).get('benefits', {}).get('FR', {}).get('categories', [])
#     return ", ".join(
#         benefit['name']['fr']
#         for category in benefits
#         for benefit in category.get('benefits', [])
#     )

# def get_skills(data):
#     skills = data.get('job', {}).get('skills', [])
#     return ", ".join(skill['name']['fr'] for skill in skills)

# def get_application_fields(data):
#     return {field['name']: field['mode'] for field in data.get('job', {}).get('application_fields', [])}

# # def extract_basic_info(offre):
# #     # org = offre['organization']
# #     # return {
# #     #     'company_name': org['name'],
# #     #     'poste': offre['name'],
# #     #     'remote': offre['remote'],
# #     #     'url': offre['urls'][0]['href'],
# #     #     'education_level': offre['education_level'],
# #     #     'salary_min': offre['salary_min'],
# #     #     'salary_max': offre['salary_max'],
# #     #     'salary_currency': offre['salary_currency'],
# #     #     'published_at': offre['published_at'],
# #     #     'industry': org['industry'],
# #     #     'company_url': org['media_website_url'],
# #     #     'description': offre['description']
# #     # }
# def extract_basic_info(offre):
#     """Extrait un maximum d'informations utiles de l'offre d'emploi."""
#     return {
#         # Infos de l'offre
#         'wttj_reference': offre.get('wttj_reference'),
#         'job_reference': offre.get('reference'),
#         'poste': offre.get('name'),
#         'description': offre.get('description'),
#         'profile': offre.get('profile'),
#         'published_at': offre.get('published_at'),
#         'updated_at': offre.get('updated_at'),

#         # Lien
#         'url': offre['urls'][0]['href'] if offre.get('urls') else None,

#         # Remote
#         'remote': offre.get('remote'),
#         'remote_policy': offre.get('remote_policy'),
#         'office_remote_ratio': offre.get('office_remote_ratio'),

#         # Localisation(s)
#         'locations': [
#             loc.get('name') for loc in offre.get('locations', [])
#         ],

#         # Contrat
#         'contract_type': offre.get('contract_type'),
#         'contract_duration_min': offre.get('contract_duration_min'),
#         'contract_duration_max': offre.get('contract_duration_max'),

#         # Salaire
#         'salary_min': offre.get('salary_min'),
#         'salary_max': offre.get('salary_max'),
#         'salary_currency': offre.get('salary_currency'),
#         'salary_period': offre.get('salary_period'),

#         # Éducation
#         'education_level': offre.get('education_level'),

#         # Processus de recrutement
#         'recruitment_process': offre.get('recruitment_process'),

#         # Profession
#         'profession': offre.get('profession', {}).get('name', {}).get('fr'),

#         # Compétences / tags
#         'tags': [
#             tag.get('name') for tag in offre.get('tags', [])
#         ],

#         # Langues
#         'languages': [
#             lang.get('code') for lang in offre.get('languages', [])
#         ],

#         # Infos entreprise
#         'company_name': offre['organization'].get('name'),
#         'industry': offre['organization'].get('industry'),
#         'creation_year': offre['organization'].get('creation_year'),
#         'nb_employees': offre['organization'].get('nb_employees'),
#         'parity_women': offre['organization'].get('parity_women'),
#         'average_age': offre['organization'].get('average_age'),
#         'company_url': offre['organization'].get('media_website_url'),
#         'company_logo': offre['organization'].get('logo'),
#         'company_description': offre['organization'].get('description'),
#     }

# def extract_offre(full_url):
#     try:
#         data = fetch_data(full_url)
#         job = data['job']
#         info = extract_basic_info(job)
#         info.update({
#             'benefits': get_benefits(data),
#             'skills': get_skills(data),
#             **get_application_fields(data)
#         })
#         return pd.DataFrame([info])
#     except Exception as e:
#         print(f"Erreur extraction {full_url}: {e}")
#         return pd.DataFrame()

# def enrich_dataset(df):
#     df['api_url'] = df['link'].apply(get_api_url)
#     full_data = []

#     for url in tqdm(df['api_url']):
#         full_data.append(extract_offre(url))

#     return pd.concat(full_data).reset_index(drop=True)
import requests
import pandas as pd
import re
from tqdm import tqdm

def _api_url(job_url):
    part = re.findall(".+/companies(.+)", job_url)[0]
    return "https://api.welcometothejungle.com/api/v1/organizations" + part

def _fetch(url):
    return requests.get(url).json()

def enrich_dataset(df_links: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for link in tqdm(df_links["link"]):
        try:
            data = _fetch(_api_url(link))
            job = data["job"]
            org = job["organization"]
            office = job.get("office", {})

            rows.append({
                # --- JOB ---
                "wttj_reference": job["wttj_reference"],
                "job_reference": job["reference"],
                "company_name": org["name"],
                "poste": job["name"],
                "remote": job["remote"],
                "url": job["urls"][0]["href"],
                "education_level": job["education_level"],
                "profile": job["profile"],
                "salary_min": job["salary_min"],
                "salary_max": job["salary_max"],
                "salary_currency": job["salary_currency"],
                "published_at": job["published_at"],
                "updated_at": job["updated_at"],
                "profession": job["profession"]["name"]["fr"],
                "contract_type": job["contract_type"],
                "contract_duration_min": job["contract_duration_min"],
                "contract_duration_max": job["contract_duration_max"],
                "salary_period": job["salary_period"],
                "recruitment_process": job["recruitment_process"],

                # --- COMPANY ---
                "industry": org["industry"],
                "creation_year": org["creation_year"],
                "parity_women": org["parity_women"],
                "nb_employees": org["nb_employees"],
                "average_age": org["average_age"],
                "company_url": org["media_website_url"],
                "company_description": job["description"],

                # --- BENEFITS / SKILLS / TOOLS ---
                "benefits": ", ".join(
                    b["name"]["fr"]
                    for c in job.get("benefits", {}).get("FR", {}).get("categories", [])
                    for b in c.get("benefits", [])
                ),
                "skills": ", ".join(s["name"]["fr"] for s in job.get("skills", [])),
                "tools": ", ".join(t["name"] for t in job.get("tools", [])),

                # --- APPLICATION ---
                **{f["name"]: f["mode"] for f in job.get("application_fields", [])},

                # --- OFFICE ---
                "address": office.get("address"),
                "local_address": office.get("local_address"),
                "city": office.get("city"),
                "latitude": office.get("latitude"),
                "longitude": office.get("longitude"),
                "country_code": office.get("country_code"),
                "zip_code": office.get("zip_code"),
                "district": office.get("district"),
                "local_district": office.get("local_district"),
                "local_city": office.get("local_city"),
            })

        except Exception:
            pass

    return pd.DataFrame(rows)
