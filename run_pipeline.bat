@echo off
REM ============================================
REM Script batch pour Windows Task Scheduler
REM ============================================
REM Ce script execute le pipeline WTTJ
REM
REM Pour configurer dans Task Scheduler:
REM 1. Ouvrir "Planificateur de taches" (taskschd.msc)
REM 2. Creer une tache de base
REM 3. Nom: "WTTJ Pipeline Hebdomadaire"
REM 4. Declencheur: Hebdomadaire, Dimanche 02:00
REM 5. Action: Demarrer un programme
REM 6. Programme: C:\Users\Utilisateur\Documents\wttj\run_pipeline.bat
REM ============================================

cd /d C:\Users\Utilisateur\Documents\wttj

REM Activer l'environnement virtuel si existant
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Executer le pipeline
python run_pipeline.py

REM Pause pour voir les erreurs (optionnel, retirer en production)
REM pause
