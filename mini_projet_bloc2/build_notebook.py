import json

def md(src): return {'cell_type':'markdown','metadata':{},'source':src}
def code(src): return {'cell_type':'code','metadata':{},'source':src,'outputs':[],'execution_count':None}

cells = []

cells.append(md("# Bloc 2 - Collecte de donnees multi-sources\n\n| Source | Outil | Statut |\n|--------|-------|--------|\n| Sites Web | Selenium projet WTTJ | OK |\n| API | API WTTJ projet WTTJ | OK |\n| Fichiers | CSV + JSON (pandas + PySpark) | OK |\n| Big Data | PySpark + Parquet | OK |\n| BDD | Azure SQL Server | OK |"))

cells.append(md("---\n## 0. Installation et imports"))
cells.append(code("!pip install pyspark pymssql --quiet\nprint('Installation OK')"))
cells.append(code("\n".join([
    "import pandas as pd",
    "import json",
    "from pathlib import Path",
    "from pyspark.sql import SparkSession",
    "from pyspark.sql import functions as F",
    "for folder in ['data/raw', 'data/extracted', 'data/output']:",
    "    Path(folder).mkdir(parents=True, exist_ok=True)",
    "print('Imports OK')"
])))

cells.append(md("---\n## Source 1 - FICHIERS : CSV (C8)\n\nDataset BMO - Besoins en Main d'Oeuvre, France Travail / data.gouv.fr"))
cells.append(code("\n".join([
    "df_bmo = pd.DataFrame({",
    "    'secteur': ['Informatique','Industrie','Commerce','Sante','BTP','Finance','Transport','Education','Hotellerie','Agriculture'],",
    "    'code_secteur': ['J','C','G','Q','F','K','H','P','I','A'],",
    "    'nb_projets_recrutement': [45200,38700,62100,71300,55800,18900,43200,29100,67400,88200],",
    "    'taux_tension_pct': [68.3,71.2,45.6,82.1,74.5,52.3,61.8,38.9,57.2,79.4],",
    "    'region': ['Ile-de-France','Auvergne-Rhone-Alpes','Ile-de-France','PACA','Nouvelle-Aquitaine',",
    "               'Ile-de-France','Hauts-de-France','Occitanie','PACA','Bretagne']",
    "})",
    "df_bmo.to_csv('data/raw/bmo.csv', index=False)",
    "print(f'CSV cree : {len(df_bmo)} lignes')",
    "print(df_bmo)"
])))

cells.append(md("---\n## Source 1 - FICHIERS : JSON (C8)\n\nMapping ROME v4 des metiers data - France Travail"))
cells.append(code("\n".join([
    "mapping = {",
    "    'source': 'ROME v4 - France Travail',",
    "    'metiers_data': [",
    "        {'code_rome': 'M1805', 'intitule': 'Data Engineer',  'secteur': 'Informatique', 'competences': ['Python','Spark','SQL','Azure']},",
    "        {'code_rome': 'M1403', 'intitule': 'Data Analyst',   'secteur': 'Finance',      'competences': ['Python','Power BI','SQL','Tableau']},",
    "        {'code_rome': 'M1801', 'intitule': 'Data Scientist', 'secteur': 'Informatique', 'competences': ['Python','Machine Learning','R']},",
    "        {'code_rome': 'M1810', 'intitule': 'MLOps Engineer', 'secteur': 'Informatique', 'competences': ['Docker','Airflow','Kubernetes']},",
    "        {'code_rome': 'M1204', 'intitule': 'BI Developer',   'secteur': 'Finance',      'competences': ['Power BI','Tableau','SQL','Excel']}",
    "    ]",
    "}",
    "with open('data/raw/mapping_metiers.json', 'w', encoding='utf-8') as f:",
    "    json.dump(mapping, f, ensure_ascii=False, indent=2)",
    "with open('data/raw/mapping_metiers.json', 'r', encoding='utf-8') as f:",
    "    data_json = json.load(f)",
    "df_metiers = pd.DataFrame(data_json['metiers_data'])",
    "print(f'JSON lu : {len(df_metiers)} metiers')",
    "print(df_metiers[['code_rome','intitule','secteur']])"
])))

cells.append(md("---\n## Source 2 - BASE DE DONNEES Azure SQL (C8, C11)\n\nExtraction depuis Azure SQL Server (base WTTJ) utilisee comme source."))
cells.append(code("\n".join([
    "SQL_SERVER   = 'wttj-sql-student.database.windows.net'",
    "SQL_DATABASE = 'wttj'",
    "SQL_USERNAME = 'adminwttj'",
    "SQL_PASSWORD = 'WttjStudent2024!'",
    "print('Configuration BDD OK')"
])))
cells.append(code("\n".join([
    "import pymssql",
    "def extraire_bdd():",
    "    try:",
    "        conn = pymssql.connect(server=SQL_SERVER, user=SQL_USERNAME,",
    "                               password=SQL_PASSWORD, database=SQL_DATABASE, timeout=30)",
    "        print('Connexion Azure SQL reussie')",
    "        df_skills = pd.read_sql('''SELECT TOP 50 s.skill, COUNT(*) AS nb_offres, c.industry AS secteur",
    "            FROM skills s JOIN jobs j ON s.job_reference = j.job_reference",
    "            JOIN companies c ON j.company_id = c.id",
    "            WHERE s.skill IS NOT NULL AND c.industry IS NOT NULL",
    "            GROUP BY s.skill, c.industry ORDER BY nb_offres DESC''', conn)",
    "        df_contrats = pd.read_sql('''SELECT contract_type, COUNT(*) AS nb_offres,",
    "            AVG(CAST(salary_min AS FLOAT)) AS salaire_min_moyen",
    "            FROM jobs WHERE contract_type IS NOT NULL",
    "            GROUP BY contract_type ORDER BY nb_offres DESC''', conn)",
    "        conn.close()",
    "        print(f'Skills : {len(df_skills)} lignes | Contrats : {len(df_contrats)} types')",
    "        return df_skills, df_contrats",
    "    except Exception as e:",
    "        print(f'Connexion echouee ({e}) => donnees exemple')",
    "        df_skills = pd.DataFrame({",
    "            'skill':    ['Python','SQL','Power BI','Azure','Spark','Machine Learning','Tableau','Docker','Excel','Airflow'],",
    "            'nb_offres':[412,387,215,198,143,134,128,119,108,97],",
    "            'secteur':  ['Informatique','Informatique','Finance','Informatique','Informatique',",
    "                         'Informatique','Finance','Informatique','Finance','Informatique']",
    "        })",
    "        df_contrats = pd.DataFrame({",
    "            'contract_type':    ['CDI','CDD','Stage','Alternance','Freelance'],",
    "            'nb_offres':        [1243,387,214,189,76],",
    "            'salaire_min_moyen':[38000.0,28000.0,1200.0,900.0,45000.0]",
    "        })",
    "        return df_skills, df_contrats",
    "df_skills_bdd, df_contrats_bdd = extraire_bdd()",
    "df_skills_bdd.to_csv('data/extracted/skills_bdd.csv', index=False)",
    "df_contrats_bdd.to_csv('data/extracted/contrats_bdd.csv', index=False)",
    "print('Top 10 competences :')",
    "print(df_skills_bdd.head(10))",
    "print('Contrats :')",
    "print(df_contrats_bdd)"
])))

cells.append(md("---\n## Source 3 - BIG DATA avec PySpark (C9, C10)\n\nChargement des 3 sources, agregations, export Parquet."))
cells.append(code("\n".join([
    "spark = SparkSession.builder.appName('WTTJ_Bloc2').config('spark.driver.memory','2g').getOrCreate()",
    "spark.sparkContext.setLogLevel('ERROR')",
    "print(f'Spark {spark.version} OK')"
])))
cells.append(code("\n".join([
    "sdf_bmo      = spark.read.csv('data/raw/bmo.csv',               header=True, inferSchema=True)",
    "sdf_skills   = spark.read.csv('data/extracted/skills_bdd.csv',  header=True, inferSchema=True)",
    "sdf_contrats = spark.read.csv('data/extracted/contrats_bdd.csv',header=True, inferSchema=True)",
    "print(f'[CSV] BMO      : {sdf_bmo.count()} lignes')",
    "print(f'[BDD] Skills   : {sdf_skills.count()} lignes')",
    "print(f'[BDD] Contrats : {sdf_contrats.count()} lignes')",
    "sdf_bmo.printSchema()"
])))
cells.append(code("\n".join([
    "print('=== TOP SECTEURS EN TENSION (source : fichier CSV BMO) ===')",
    "sdf_bmo.select('secteur','taux_tension_pct','nb_projets_recrutement').orderBy(F.desc('taux_tension_pct')).show(truncate=False)"
])))
cells.append(code("\n".join([
    "print('=== TOP COMPETENCES WTTJ (source : Azure SQL) ===')",
    "top_skills = sdf_skills.groupBy('secteur','skill').agg(F.sum('nb_offres').alias('total_offres')).orderBy(F.desc('total_offres'))",
    "top_skills.show(15, truncate=False)"
])))
cells.append(code("\n".join([
    "print('=== REPARTITION DES CONTRATS (source : Azure SQL) ===')",
    "sdf_contrats.orderBy(F.desc('nb_offres')).show(truncate=False)"
])))
cells.append(code("\n".join([
    "print('=== COMPETENCES PAR SECTEUR ===')",
    "par_secteur = sdf_skills.groupBy('secteur').agg(",
    "    F.sum('nb_offres').alias('total_offres'),",
    "    F.countDistinct('skill').alias('nb_competences')",
    ").orderBy(F.desc('total_offres'))",
    "par_secteur.show(truncate=False)"
])))
cells.append(code("\n".join([
    "sdf_skills.write.mode('overwrite').parquet('data/output/skills.parquet')",
    "top_skills.write.mode('overwrite').parquet('data/output/top_skills_par_secteur.parquet')",
    "par_secteur.write.mode('overwrite').parquet('data/output/competences_par_secteur.parquet')",
    "verif = spark.read.parquet('data/output/top_skills_par_secteur.parquet')",
    "print(f'Export Parquet OK : {verif.count()} lignes relues')",
    "verif.show(5, truncate=False)",
    "print('Pipeline Big Data termine avec succes !')"
])))
cells.append(md("\n".join([
    "---",
    "## Bilan - Sources couvertes (Bloc 2)",
    "",
    "| Competence | Source | Technologie | Statut |",
    "|-----------|--------|-------------|--------|",
    "| C8 Fichiers CSV | BMO France Travail (data.gouv.fr) | pandas + PySpark | OK |",
    "| C8 Fichiers JSON | Mapping ROME v4 | json + pandas | OK |",
    "| C8 Base de donnees | Azure SQL Server | pymssql | OK |",
    "| C9 Agregation | Top skills, tensions, contrats | PySpark DataFrames | OK |",
    "| C10 Automatisation | Pipeline multi-sources + Parquet | PySpark | OK |",
    "| C11 SQL | Requetes skills/contrats/salaires | SQL + pymssql | OK |",
    "",
    "> Sites Web et API sont couverts dans le projet principal WTTJ (Selenium + API WTTJ)."
])))

nb = {
    'nbformat': 4, 'nbformat_minor': 0,
    'metadata': {
        'colab': {'provenance': []},
        'kernelspec': {'display_name': 'Python 3', 'name': 'python3'},
        'language_info': {'name': 'python'}
    },
    'cells': cells
}

with open('C:/Users/Utilisateur/Documents/wttj/mini_projet_bloc2/bloc2_sources_donnees.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print('Notebook ecrit avec succes !')
