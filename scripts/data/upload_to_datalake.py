"""
Upload vers Azure Data Lake Gen2
=================================
Gère l'upload des fichiers CSV vers les zones du data lake :
  - Zone RAW    : wttj/raw/YYYY-MM-DD/data.csv
  - Zone CURATED: wttj/curated/YYYY-MM-DD/jobs_clean.csv
  - Zone LOGS   : wttj/logs/YYYY-MM-DD/pipeline.log

Usage autonome :
    python scripts/data/upload_to_datalake.py --zone raw --file data/data.csv
    python scripts/data/upload_to_datalake.py --zone curated --file data/jobs_clean.csv
    python scripts/data/upload_to_datalake.py --zone all
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.core.exceptions import AzureError

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

STORAGE_ACCOUNT = os.getenv("STORAGE_ACCOUNT", "adlswttjstudent")
ACCOUNT_KEY = os.getenv("ACCOUNT_KEY")
CONTAINER_NAME = os.getenv("CONTAINER_NAME", "wttj")

ACCOUNT_URL = f"https://{STORAGE_ACCOUNT}.blob.core.windows.net"

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_client() -> BlobServiceClient:
    """Crée un client BlobService authentifié par clé de compte."""
    if not ACCOUNT_KEY:
        raise EnvironmentError(
            "ACCOUNT_KEY manquant dans .env — "
            "récupère la clé dans Azure Portal > Storage Account > Access Keys"
        )
    return BlobServiceClient(account_url=ACCOUNT_URL, credential=ACCOUNT_KEY)


def _upload_file(local_path: Path, blob_path: str, overwrite: bool = True) -> bool:
    """
    Upload un fichier local vers ADLS Gen2.

    Args:
        local_path : chemin local du fichier à uploader
        blob_path  : chemin destination dans le container (ex: raw/2025-01-21/data.csv)
        overwrite  : écrase le fichier existant si True

    Returns:
        True si succès, False sinon
    """
    if not local_path.exists():
        logger.error(f"Fichier introuvable : {local_path}")
        return False

    try:
        client = _get_client()
        blob_client: BlobClient = client.get_blob_client(
            container=CONTAINER_NAME, blob=blob_path
        )

        file_size = local_path.stat().st_size
        logger.info(f"Upload : {local_path} → {CONTAINER_NAME}/{blob_path} ({file_size:,} octets)")

        with open(local_path, "rb") as f:
            blob_client.upload_blob(f, overwrite=overwrite)

        logger.info(f"Upload réussi : {ACCOUNT_URL}/{CONTAINER_NAME}/{blob_path}")
        return True

    except AzureError as e:
        logger.error(f"Erreur Azure lors de l'upload de {local_path} : {e}")
        return False
    except Exception as e:
        logger.error(f"Erreur inattendue lors de l'upload de {local_path} : {e}")
        return False


# ---------------------------------------------------------------------------
# Fonctions publiques (appelées par run_pipeline.py)
# ---------------------------------------------------------------------------

def upload_raw(raw_csv: Path, date_str: str = None) -> bool:
    """
    Upload le CSV brut vers la zone RAW du data lake.

    Structure : wttj/raw/YYYY-MM-DD/data.csv

    Args:
        raw_csv  : chemin local vers data.csv
        date_str : date au format YYYY-MM-DD (défaut = aujourd'hui)
    """
    date_str = date_str or datetime.now().strftime("%Y-%m-%d")
    blob_path = f"raw/{date_str}/data.csv"
    logger.info(f"[DATALAKE] Zone RAW — {blob_path}")
    return _upload_file(raw_csv, blob_path)


def upload_curated(curated_csv: Path, date_str: str = None) -> bool:
    """
    Upload le CSV nettoyé vers la zone CURATED du data lake.

    Structure : wttj/curated/YYYY-MM-DD/jobs_clean.csv

    Args:
        curated_csv : chemin local vers jobs_clean.csv
        date_str    : date au format YYYY-MM-DD (défaut = aujourd'hui)
    """
    date_str = date_str or datetime.now().strftime("%Y-%m-%d")
    blob_path = f"curated/{date_str}/jobs_clean.csv"
    logger.info(f"[DATALAKE] Zone CURATED — {blob_path}")
    return _upload_file(curated_csv, blob_path)


def upload_log(log_file: Path, date_str: str = None) -> bool:
    """
    Upload le fichier de log vers la zone LOGS du data lake.

    Structure : wttj/logs/YYYY-MM-DD/pipeline.log

    Args:
        log_file : chemin local vers le log du pipeline
        date_str : date au format YYYY-MM-DD (défaut = aujourd'hui)
    """
    date_str = date_str or datetime.now().strftime("%Y-%m-%d")
    blob_path = f"logs/{date_str}/pipeline.log"
    logger.info(f"[DATALAKE] Zone LOGS — {blob_path}")
    return _upload_file(log_file, blob_path)


# ---------------------------------------------------------------------------
# CLI autonome
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Upload vers Azure Data Lake Gen2 WTTJ")
    parser.add_argument(
        "--zone",
        choices=["raw", "curated", "logs", "all"],
        required=True,
        help="Zone du data lake cible"
    )
    parser.add_argument("--file", type=Path, help="Fichier à uploader (non requis pour --zone all)")
    parser.add_argument("--date", help="Date YYYY-MM-DD (défaut = aujourd'hui)")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    project_root = Path(__file__).resolve().parents[2]

    if args.zone == "raw":
        target = args.file or (project_root / "data" / "data.csv")
        success = upload_raw(target, args.date)

    elif args.zone == "curated":
        target = args.file or (project_root / "data" / "jobs_clean.csv")
        success = upload_curated(target, args.date)

    elif args.zone == "logs":
        if not args.file:
            print("--file requis pour --zone logs")
            sys.exit(1)
        success = upload_log(args.file, args.date)

    else:  # all
        date_str = args.date or datetime.now().strftime("%Y-%m-%d")
        r1 = upload_raw(project_root / "data" / "data.csv", date_str)
        r2 = upload_curated(project_root / "data" / "jobs_clean.csv", date_str)
        success = r1 and r2

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
