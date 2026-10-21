@echo off
setlocal enabledelayedexpansion

cd /d "C:\Users\Carlos Enyerve\Desktop\PROYECTOS\MET"

echo ====================================================== >> respaldo_log.txt
echo Respaldo iniciado: %DATE% %TIME% >> respaldo_log.txt

git status --porcelain > temp_status.txt
set /p CAMBIOS=<temp_status.txt
del temp_status.txt

if defined CAMBIOS (
    echo Cambios detectados. Guardando y subiendo... >> respaldo_log.txt
    git add . >> respaldo_log.txt 2>&1
    git commit -m "Auto-backup: %DATE% %TIME%" >> respaldo_log.txt 2>&1
    git push origin main >> respaldo_log.txt 2>&1
    echo Respaldo completado con exito. >> respaldo_log.txt
) else (
    echo No hay cambios nuevos para respaldar. >> respaldo_log.txt
)

echo ====================================================== >> respaldo_log.txt
