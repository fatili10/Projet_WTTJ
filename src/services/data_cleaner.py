import pandas as pd
from bs4 import BeautifulSoup
import math
import numpy as np


def fix_nan(value):
    if isinstance(value, float) and math.isnan(value):
        return None
    return value

def clean_html(text):
    """
    Enlève les balises HTML et retourne le texte propre.
    Si la valeur est NaN, renvoie une chaîne vide.
    """
    if pd.isna(text):
        return ""
    return BeautifulSoup(text, "html.parser").get_text().strip()

def nettoyage_jobs(input_path, output_path):
    # Chargement du CSV d'origine
    df = pd.read_csv(input_path)
    print(f"Shape initiale : {df.shape}")
    print(f"Colonnes chargées : {list(df.columns)}")

    # Colonnes contenant potentiellement du HTML à nettoyer
    colonnes_html = ['recruitment_process', 'profile', 'company_description', 'benefits']

    # Nettoyage HTML sur les colonnes ciblées
    for col in colonnes_html:
        if col in df.columns:
            print(f"Nettoyage HTML sur la colonne '{col}'...")
            df[col] = df[col].apply(clean_html)

    # Suppression des lignes sans 'poste' ou 'company_name'
    df = df.dropna(subset=['poste', 'company_name'])

    # Suppression des doublons exacts
    df = df.drop_duplicates()

    # Conversion des colonnes dates en datetime, suppression des valeurs invalides
    df['published_at'] = pd.to_datetime(df['published_at'], errors='coerce')
    df['updated_at'] = pd.to_datetime(df['updated_at'], errors='coerce')
    df = df.dropna(subset=['published_at'])

    # Colonnes numériques où remplacer NaN par None (valeur NULL en base)
    colonnes_numeriques = [
        'salary_min', 'salary_max',
        'contract_duration_min', 'contract_duration_max'
    ]
    for col in colonnes_numeriques:
        if col in df.columns:
            df[col] = df[col].apply(fix_nan)

    # Réinitialisation de l'index
    df = df.reset_index(drop=True)

    print(f"Shape après nettoyage : {df.shape}")

    # Sauvegarde dans un fichier CSV nettoyé
    df.to_csv(output_path, index=False)
    print(f"Fichier nettoyé enregistré dans : {output_path}")

if __name__ == "__main__":
    input_csv = "data/data.csv"  
    output_csv = "data/jobs_clean.csv"

    nettoyage_jobs(input_csv, output_csv)




# def fix_nan(value):
#     if isinstance(value, float) and math.isnan(value):
#         return None
#     return value

# def fix_nan_in_job(job):
#     """
#     Remplace tous les attributs numériques de l'objet job égaux à nan par None.
#     Modifie l'objet job en place et retourne None.
#     """
#     job.salary_min = fix_nan(job.salary_min)
#     job.salary_max = fix_nan(job.salary_max)
#     job.contract_duration_min = fix_nan(job.contract_duration_min)
#     job.contract_duration_max = fix_nan(job.contract_duration_max)
#     job.office_remote_ratio = fix_nan(job.office_remote_ratio)

# def clean_html(text):
#     """
#     Enlève les balises HTML et retourne le texte propre.
#     Si la valeur est NaN, renvoie une chaîne vide.
#     """
#     if pd.isna(text):
#         return ""
#     return BeautifulSoup(text, "html.parser").get_text().strip()

# def nettoyage_jobs(input_path, output_path):
#     # Chargement du CSV d'origine
#     df = pd.read_csv(input_path)
#     print(f"Shape initiale : {df.shape}")
#     print(f"Colonnes chargées : {list(df.columns)}")

#     # Colonnes contenant potentiellement du HTML à nettoyer
#     colonnes_html = ['description', 'profile', 'company_description', 'benefits']

#     # Nettoyage HTML sur les colonnes ciblées
#     for col in colonnes_html:
#         if col in df.columns:
#             print(f"Nettoyage HTML sur la colonne '{col}'...")
#             df[col] = df[col].apply(clean_html)

#     # Suppression des lignes sans 'poste' ou 'company_name'
#     df = df.dropna(subset=['poste', 'company_name'])

#     # Suppression des doublons exacts
#     df = df.drop_duplicates()

#     # Conversion des colonnes dates en datetime, suppression des valeurs invalides
#     df['published_at'] = pd.to_datetime(df['published_at'], errors='coerce')
#     df['updated_at'] = pd.to_datetime(df['updated_at'], errors='coerce')
#     df = df.dropna(subset=['published_at'])

#     # Réinitialisation de l'index
#     df = df.reset_index(drop=True)

#     print(f"Shape après nettoyage : {df.shape}")

#     # Sauvegarde dans un fichier CSV nettoyé
#     df.to_csv(output_path, index=False)
#     print(f"Fichier nettoyé enregistré dans : {output_path}")

# if __name__ == "__main__":
#     # Modifier ici les chemins vers tes fichiers CSV
#     input_csv = "data/data.csv"  
#     output_csv = "data/jobs_clean.csv"

#     nettoyage_jobs(input_csv, output_csv)
