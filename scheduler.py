"""
Scheduler WTTJ - Exécution hebdomadaire automatique
===================================================
Ce script planifie l'exécution du pipeline chaque semaine.

Options d'utilisation:
1. Exécuter ce script en arrière-plan (il tourne en continu)
2. Utiliser Windows Task Scheduler avec run_pipeline.bat

Configuration par défaut:
- Jour: Dimanche
- Heure: 02:00 (pour éviter les pics de charge)

Usage:
    python scheduler.py                    # Démarre le scheduler
    python scheduler.py --day monday       # Change le jour
    python scheduler.py --time 08:00       # Change l'heure
    python scheduler.py --run-now          # Exécute immédiatement
"""
import schedule
import time
import logging
import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Configuration du logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "scheduler.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration par défaut
DEFAULT_DAY = "sunday"
DEFAULT_TIME = "02:00"


def run_pipeline():
    """Exécute le pipeline WTTJ"""
    logger.info("=" * 60)
    logger.info("SCHEDULER: Démarrage du pipeline automatique")
    logger.info(f"Date/Heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    try:
        # Exécuter run_pipeline.py
        result = subprocess.run(
            [sys.executable, "run_pipeline.py"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )

        if result.returncode == 0:
            logger.info("SCHEDULER: Pipeline terminé avec succès")
        else:
            logger.error(f"SCHEDULER: Pipeline échoué (code: {result.returncode})")
            if result.stderr:
                logger.error(f"Erreur: {result.stderr[:500]}")

        return result.returncode == 0

    except Exception as e:
        logger.error(f"SCHEDULER: Erreur lors de l'exécution: {e}")
        return False


def setup_schedule(day: str, time_str: str):
    """Configure la planification"""
    day = day.lower()

    day_mapping = {
        "monday": schedule.every().monday,
        "tuesday": schedule.every().tuesday,
        "wednesday": schedule.every().wednesday,
        "thursday": schedule.every().thursday,
        "friday": schedule.every().friday,
        "saturday": schedule.every().saturday,
        "sunday": schedule.every().sunday,
        "lundi": schedule.every().monday,
        "mardi": schedule.every().tuesday,
        "mercredi": schedule.every().wednesday,
        "jeudi": schedule.every().thursday,
        "vendredi": schedule.every().friday,
        "samedi": schedule.every().saturday,
        "dimanche": schedule.every().sunday,
    }

    if day not in day_mapping:
        logger.error(f"Jour invalide: {day}")
        logger.info(f"Jours valides: {', '.join(day_mapping.keys())}")
        sys.exit(1)

    day_mapping[day].at(time_str).do(run_pipeline)
    logger.info(f"Pipeline planifié: chaque {day} à {time_str}")


def main():
    parser = argparse.ArgumentParser(
        description="Scheduler WTTJ - Planification hebdomadaire"
    )
    parser.add_argument(
        '--day', '-d',
        default=DEFAULT_DAY,
        help=f'Jour de la semaine (défaut: {DEFAULT_DAY})'
    )
    parser.add_argument(
        '--time', '-t',
        default=DEFAULT_TIME,
        help=f'Heure d\'exécution HH:MM (défaut: {DEFAULT_TIME})'
    )
    parser.add_argument(
        '--run-now', '-r',
        action='store_true',
        help='Exécute le pipeline immédiatement'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Mode test: exécute toutes les minutes'
    )

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("WTTJ SCHEDULER - Démarrage")
    logger.info("=" * 60)

    # Exécution immédiate si demandé
    if args.run_now:
        logger.info("Exécution immédiate demandée...")
        run_pipeline()
        return

    # Mode test (toutes les minutes)
    if args.test:
        logger.info("MODE TEST: Exécution toutes les minutes")
        schedule.every(1).minutes.do(run_pipeline)
    else:
        # Configuration normale
        setup_schedule(args.day, args.time)

    logger.info("Scheduler démarré. Appuyez sur Ctrl+C pour arrêter.")
    logger.info(f"Prochaine exécution: {schedule.next_run()}")

    # Boucle principale
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Vérifie toutes les minutes
    except KeyboardInterrupt:
        logger.info("\nScheduler arrêté par l'utilisateur")
        sys.exit(0)


if __name__ == "__main__":
    main()
