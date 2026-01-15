#!/bin/bash
#
# Script de Backup Automatique
# À ajouter dans crontab:
# 0 2 * * * /path/to/backup-cron.sh
#

# Configuration
PROJECT_DIR="/path/to/ggr-credit-workflow"
PYTHON_PATH="/path/to/venv/bin/python"
LOG_FILE="$PROJECT_DIR/logs/backup.log"

# Créer le dossier logs
mkdir -p "$PROJECT_DIR/logs"

# Timestamp
echo "=== Backup $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG_FILE"

# Activer l'environnement virtuel
cd "$PROJECT_DIR"

# Exécuter le backup
$PYTHON_PATH manage.py backup_db --compress --upload-s3 >> "$LOG_FILE" 2>&1

# Vérifier le résultat
if [ $? -eq 0 ]; then
    echo "✅ Backup réussi" >> "$LOG_FILE"
else
    echo "❌ Backup échoué" >> "$LOG_FILE"
    # Envoyer une alerte email
    echo "Backup failed at $(date)" | mail -s "Backup Error" admin@example.com
fi

echo "" >> "$LOG_FILE"
