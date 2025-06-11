@echo off
echo 🔍 DETECTOR AUTOMATICO DE BALANZA
echo ================================
echo.
echo Iniciando detector de balanza...
python detector_balanza.py
echo.
echo ¿Desea aplicar la configuracion detectada? (S/N)
set /p aplicar=
if /i "%aplicar%"=="S" (
    echo.
    echo Aplicando configuracion...
    python aplicar_configuracion_detectada.py
)
echo.
pause
