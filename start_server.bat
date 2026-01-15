@echo off
echo Demarrage du serveur GGR Credit Workflow...
echo.

REM Definir les variables d'environnement
set ALLOWED_HOSTS=localhost,127.0.0.1,pro.ggr-credit.local,client.ggr-credit.local
set DJANGO_SETTINGS_MODULE=core.settings

echo Configuration:
echo - ALLOWED_HOSTS: %ALLOWED_HOSTS%
echo - Port: 8002
echo.

REM Demarrer le serveur
python manage.py runserver 0.0.0.0:8002
