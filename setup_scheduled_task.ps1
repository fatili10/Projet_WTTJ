# ============================================
# Script PowerShell pour creer la tache planifiee
# ============================================
# Executer en tant qu'administrateur:
# PowerShell -ExecutionPolicy Bypass -File setup_scheduled_task.ps1
# ============================================

$taskName = "WTTJ_Pipeline_Hebdomadaire"
$taskDescription = "Execute le pipeline de scraping WTTJ chaque semaine"
$scriptPath = "C:\Users\Utilisateur\Documents\wttj\run_pipeline.bat"
$workingDir = "C:\Users\Utilisateur\Documents\wttj"

# Supprimer la tache si elle existe deja
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "Suppression de l'ancienne tache..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Configuration du declencheur (Dimanche a 02:00)
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 2:00AM

# Configuration de l'action
$action = New-ScheduledTaskAction -Execute $scriptPath -WorkingDirectory $workingDir

# Configuration des parametres
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -WakeToRun

# Creation de la tache
Register-ScheduledTask `
    -TaskName $taskName `
    -Description $taskDescription `
    -Trigger $trigger `
    -Action $action `
    -Settings $settings `
    -RunLevel Highest

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Tache planifiee creee avec succes!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Nom: $taskName"
Write-Host "Execution: Chaque Dimanche a 02:00"
Write-Host "Script: $scriptPath"
Write-Host ""
Write-Host "Pour modifier: taskschd.msc" -ForegroundColor Cyan
Write-Host "Pour executer manuellement: schtasks /run /tn '$taskName'" -ForegroundColor Cyan
