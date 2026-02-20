"""
Pipeline automatisé WTTJ
========================
Ce script orchestre le processus complet:
1. Scraping des offres d'emploi
2. Nettoyage des données CSV
3. Insertion en base de données
4. Archivage/nettoyage des fichiers temporaires

Usage:
    python run_pipeline.py           # Exécution complète
    python run_pipeline.py --clean   # Nettoyage + insertion seulement
    python run_pipeline.py --insert  # Insertion seulement
"""
import os
import sys
import shutil
import logging
from datetime import datetime
from pathlib import Path

# Configuration du logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
log_file = LOG_DIR / f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Chemins des fichiers
DATA_DIR = Path("data")
ARCHIVE_DIR = Path("data/archive")
RAW_CSV = DATA_DIR / "data.csv"
CLEAN_CSV = DATA_DIR / "jobs_clean.csv"


def setup_directories():
    """Crée les répertoires nécessaires"""
    DATA_DIR.mkdir(exist_ok=True)
    ARCHIVE_DIR.mkdir(exist_ok=True)
    logger.info("Répertoires créés/vérifiés")


def run_scraper():
    """Exécute le scraping des offres d'emploi"""
    logger.info("=" * 50)
    logger.info("ÉTAPE 1: SCRAPING DES OFFRES")
    logger.info("=" * 50)

    try:
        from config import COUNTRY, COUNTRY_CODE, KEYWORDS
        from src.scrapper.job_scraper import get_all_data
        from src.scrapper.api_scraper import enrich_dataset
        import pandas as pd

        all_jobs = []
        for kw in KEYWORDS:
            logger.info(f"Scraping pour le mot-clé: {kw}")
            try:
                df = get_all_data(kw, COUNTRY, COUNTRY_CODE)
                all_jobs.append(df)
                logger.info(f"  -> {len(df)} offres trouvées")
            except Exception as e:
                logger.warning(f"  -> Erreur pour '{kw}': {e}")
                continue

        if not all_jobs:
            logger.error("Aucune offre collectée!")
            return False

        df_links = pd.concat(all_jobs).reset_index(drop=True)
        logger.info(f"Total liens collectés: {len(df_links)}")

        # Suppression des doublons de liens
        df_links = df_links.drop_duplicates(subset=['link'])
        logger.info(f"Liens uniques: {len(df_links)}")

        logger.info("Enrichissement via API WTTJ...")
        df_details = enrich_dataset(df_links)

        # Sauvegarde
        df_details.to_csv(RAW_CSV, index=False)
        logger.info(f"Export terminé: {RAW_CSV}")
        logger.info(f"Nombre total d'offres: {len(df_details)}")

        return True

    except Exception as e:
        logger.error(f"Erreur lors du scraping: {e}")
        return False


def run_cleaning():
    """Nettoie les données CSV"""
    logger.info("=" * 50)
    logger.info("ÉTAPE 2: NETTOYAGE DES DONNÉES")
    logger.info("=" * 50)

    if not RAW_CSV.exists():
        logger.error(f"Fichier source introuvable: {RAW_CSV}")
        return False

    try:
        from src.services.data_cleaner import nettoyage_jobs

        nettoyage_jobs(str(RAW_CSV), str(CLEAN_CSV))
        logger.info(f"Nettoyage terminé: {CLEAN_CSV}")

        return True

    except Exception as e:
        logger.error(f"Erreur lors du nettoyage: {e}")
        return False


def run_upload_datalake(zone: str) -> bool:
    """Upload le CSV vers la zone correspondante du data lake Azure"""
    logger.info("=" * 50)
    logger.info(f"ÉTAPE DATA LAKE: UPLOAD ZONE {zone.upper()}")
    logger.info("=" * 50)

    try:
        from scripts.data.upload_to_datalake import upload_raw, upload_curated

        date_str = datetime.now().strftime("%Y-%m-%d")

        if zone == "raw":
            success = upload_raw(RAW_CSV, date_str)
        elif zone == "curated":
            success = upload_curated(CLEAN_CSV, date_str)
        else:
            logger.error(f"Zone inconnue : {zone}")
            return False

        if success:
            logger.info(f"Upload {zone} terminé avec succès")
        else:
            logger.warning(f"Upload {zone} échoué — pipeline continue")
        return success

    except Exception as e:
        logger.warning(f"Upload data lake non critique — pipeline continue : {e}")
        return False


def run_insertion():
    """Insère les données en base"""
    logger.info("=" * 50)
    logger.info("ÉTAPE 3: INSERTION EN BASE DE DONNÉES")
    logger.info("=" * 50)

    if not CLEAN_CSV.exists():
        logger.error(f"Fichier nettoyé introuvable: {CLEAN_CSV}")
        return False

    try:
        import pandas as pd
        from sqlalchemy.orm import sessionmaker
        from src.database.db import engine
        from src.database.models import Company, Location, Job, Media, Skill, Tool, Benefit

        Session = sessionmaker(bind=engine)
        session = Session()

        df = pd.read_csv(CLEAN_CSV)
        logger.info(f"Lignes à traiter: {len(df)}")

        # Remplacer NaN par None
        df = df.replace({pd.NA: None, pd.NaT: None})
        df = df.where(pd.notna(df), None)

        # Récupérer les jobs existants
        existing_jobs = set(r[0] for r in session.query(Job.job_reference).all())
        logger.info(f"Jobs existants en base: {len(existing_jobs)}")

        # Filtrer les nouveaux jobs
        new_jobs_df = df[~df['job_reference'].isin(existing_jobs)]
        logger.info(f"Nouveaux jobs à insérer: {len(new_jobs_df)}")

        if len(new_jobs_df) == 0:
            logger.info("Aucun nouveau job à insérer")
            session.close()
            return True

        # Import des fonctions utilitaires
        from scripts.data.insert_clean_data import (
            safe_get, parse_int, parse_float, parse_bool, parse_datetime
        )

        company_cache = {c.name: c for c in session.query(Company).all()}
        location_cache = {f"{l.city}_{l.zip_code}": l for l in session.query(Location).all()}

        added_jobs = 0
        for idx, row in new_jobs_df.iterrows():
            job_ref = safe_get(row, 'job_reference')
            if not job_ref:
                continue

            # Company
            company_name = safe_get(row, 'company_name')
            if company_name and company_name not in company_cache:
                company = Company(
                    name=company_name,
                    industry=safe_get(row, 'industry'),
                    creation_year=parse_int(safe_get(row, 'creation_year')),
                    parity_women=safe_get(row, 'parity_women'),
                    nb_employees=parse_int(safe_get(row, 'nb_employees')),
                    average_age=parse_float(safe_get(row, 'average_age')),
                    url=safe_get(row, 'company_url'),
                    description=safe_get(row, 'company_description')
                )
                session.add(company)
                session.flush()
                company_cache[company_name] = company
            company = company_cache.get(company_name)

            # Location
            city = safe_get(row, 'city')
            zip_code = safe_get(row, 'zip_code')
            location_key = f"{city}_{zip_code}"
            if city and location_key not in location_cache:
                location = Location(
                    address=safe_get(row, 'address'),
                    local_address=safe_get(row, 'local_address'),
                    city=city,
                    zip_code=zip_code,
                    district=safe_get(row, 'district'),
                    latitude=parse_float(safe_get(row, 'latitude')),
                    longitude=parse_float(safe_get(row, 'longitude')),
                    country_code=safe_get(row, 'country_code'),
                    local_city=safe_get(row, 'local_city'),
                    local_district=safe_get(row, 'local_district')
                )
                session.add(location)
                session.flush()
                location_cache[location_key] = location
            location = location_cache.get(location_key)

            # Job
            job = Job(
                job_reference=job_ref,
                wttj_reference=safe_get(row, 'wttj_reference'),
                poste=safe_get(row, 'poste'),
                remote=safe_get(row, 'remote'),
                url=safe_get(row, 'url'),
                education_level=safe_get(row, 'education_level'),
                profile=safe_get(row, 'profile'),
                salary_min=parse_int(safe_get(row, 'salary_min')),
                salary_max=parse_int(safe_get(row, 'salary_max')),
                salary_currency=safe_get(row, 'salary_currency'),
                salary_period=safe_get(row, 'salary_period'),
                published_at=parse_datetime(safe_get(row, 'published_at')),
                updated_at=parse_datetime(safe_get(row, 'updated_at')),
                profession=safe_get(row, 'profession'),
                contract_type=safe_get(row, 'contract_type'),
                contract_duration_min=safe_get(row, 'contract_duration_min'),
                contract_duration_max=safe_get(row, 'contract_duration_max'),
                recruitment_process=safe_get(row, 'recruitment_process'),
                cover_letter=parse_bool(safe_get(row, 'cover_letter')),
                resume=parse_bool(safe_get(row, 'resume')),
                portfolio=parse_bool(safe_get(row, 'portfolio')),
                picture=parse_bool(safe_get(row, 'picture')),
                company_id=company.id if company else None,
                location_id=location.id if location else None
            )
            session.add(job)

            # Media
            session.add(Media(
                job_reference=job_ref,
                website=safe_get(row, 'media_website'),
                linkedin=safe_get(row, 'media_linkedin'),
                twitter=safe_get(row, 'media_twitter'),
                github=safe_get(row, 'media_github'),
                stackoverflow=safe_get(row, 'media_stackoverflow'),
                behance=safe_get(row, 'media_behance'),
                dribbble=safe_get(row, 'media_dribbble'),
                xing=safe_get(row, 'media_xing')
            ))

            # Skills
            skills_str = safe_get(row, 'skills')
            if skills_str:
                for skill in str(skills_str).split(','):
                    skill = skill.strip()
                    if skill:
                        session.add(Skill(job_reference=job_ref, skill=skill))

            # Tools
            tools_str = safe_get(row, 'tools')
            if tools_str:
                for tool in str(tools_str).split(','):
                    tool = tool.strip()
                    if tool:
                        session.add(Tool(job_reference=job_ref, tool=tool))

            # Benefits
            benefits_str = safe_get(row, 'benefits')
            if benefits_str:
                for benefit in str(benefits_str).split(','):
                    benefit = benefit.strip()
                    if benefit:
                        session.add(Benefit(job_reference=job_ref, benefit=benefit))

            added_jobs += 1

        session.commit()
        logger.info(f"Jobs insérés: {added_jobs}")

        # Statistiques finales
        logger.info("=== STATISTIQUES FINALES ===")
        logger.info(f"Companies: {session.query(Company).count()}")
        logger.info(f"Locations: {session.query(Location).count()}")
        logger.info(f"Jobs: {session.query(Job).count()}")
        logger.info(f"Skills: {session.query(Skill).count()}")
        logger.info(f"Tools: {session.query(Tool).count()}")
        logger.info(f"Benefits: {session.query(Benefit).count()}")

        session.close()
        return True

    except Exception as e:
        logger.error(f"Erreur lors de l'insertion: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def cleanup_files():
    """Archive et nettoie les fichiers CSV temporaires"""
    logger.info("=" * 50)
    logger.info("ÉTAPE 4: NETTOYAGE DES FICHIERS")
    logger.info("=" * 50)

    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Archiver le CSV brut
        if RAW_CSV.exists():
            archive_name = ARCHIVE_DIR / f"data_{timestamp}.csv"
            shutil.move(str(RAW_CSV), str(archive_name))
            logger.info(f"Archivé: {RAW_CSV} -> {archive_name}")

        # Archiver le CSV nettoyé
        if CLEAN_CSV.exists():
            archive_name = ARCHIVE_DIR / f"jobs_clean_{timestamp}.csv"
            shutil.move(str(CLEAN_CSV), str(archive_name))
            logger.info(f"Archivé: {CLEAN_CSV} -> {archive_name}")

        # Supprimer les anciennes archives (garder les 4 dernières semaines)
        archives = sorted(ARCHIVE_DIR.glob("*.csv"), key=os.path.getmtime, reverse=True)
        if len(archives) > 8:  # 4 semaines * 2 fichiers
            for old_archive in archives[8:]:
                old_archive.unlink()
                logger.info(f"Supprimé (ancien): {old_archive}")

        logger.info("Nettoyage terminé")
        return True

    except Exception as e:
        logger.error(f"Erreur lors du nettoyage: {e}")
        return False


def run_full_pipeline():
    """Exécute le pipeline complet"""
    logger.info("=" * 60)
    logger.info("DÉMARRAGE DU PIPELINE WTTJ")
    logger.info(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    setup_directories()

    success = True

    # Étape 1: Scraping
    if not run_scraper():
        logger.error("Échec du scraping - Pipeline interrompu")
        success = False

    # Étape 1b: Upload zone RAW vers ADLS
    if success:
        run_upload_datalake("raw")

    # Étape 2: Nettoyage
    if success and not run_cleaning():
        logger.error("Échec du nettoyage - Pipeline interrompu")
        success = False

    # Étape 2b: Upload zone CURATED vers ADLS
    if success:
        run_upload_datalake("curated")

    # Étape 3: Insertion (zone SERVING = Azure SQL Server)
    if success and not run_insertion():
        logger.error("Échec de l'insertion - Pipeline interrompu")
        success = False

    # Étape 4: Nettoyage fichiers (même en cas d'erreur partielle)
    cleanup_files()

    logger.info("=" * 60)
    if success:
        logger.info("PIPELINE TERMINÉ AVEC SUCCÈS")
    else:
        logger.info("PIPELINE TERMINÉ AVEC ERREURS")
    logger.info("=" * 60)

    return success


def main():
    """Point d'entrée principal"""
    import argparse

    parser = argparse.ArgumentParser(description="Pipeline WTTJ automatisé")
    parser.add_argument('--clean', action='store_true',
                        help='Exécuter seulement nettoyage + insertion')
    parser.add_argument('--insert', action='store_true',
                        help='Exécuter seulement l\'insertion')
    parser.add_argument('--no-cleanup', action='store_true',
                        help='Ne pas archiver/supprimer les CSV')

    args = parser.parse_args()

    setup_directories()

    if args.insert:
        success = run_insertion()
    elif args.clean:
        success = run_cleaning() and run_insertion()
    else:
        success = run_full_pipeline()

    if not args.no_cleanup and not args.insert:
        cleanup_files()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
