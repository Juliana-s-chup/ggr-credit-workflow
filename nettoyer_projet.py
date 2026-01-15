#!/usr/bin/env python
"""Script de nettoyage automatique du projet."""
import os
import shutil

print("🧹 NETTOYAGE DU PROJET")
print("=" * 60)

# 1. Nettoyer documentation
print("\n📋 1. Nettoyage documentation...")
essentiels = [
    "GUIDE_UTILISATEUR.md", "DOCKER_GUIDE.md", "PRODUCTION_READY_GUIDE.md",
    "CHAPITRE_6.5_DATA_ANALYST.md", "AUDIT_COMPLET_PROJET.md",
    "RAPPORT_AUDIT_FINAL.md", "PLAN_AMELIORATION_COMPLET.md"
]

if not os.path.exists("docs/archive"):
    os.makedirs("docs/archive")

moved = 0
for file in os.listdir("docs"):
    if file.endswith(".md") and file not in essentiels:
        shutil.move(f"docs/{file}", f"docs/archive/{file}")
        print(f"  📦 {file}")
        moved += 1

print(f"✅ {moved} fichiers archivés\n")

# 2. Nettoyer fichiers racine
print("📋 2. Nettoyage fichiers racine...")
a_supprimer = [
    "test_logging.py", "TOUT_FONCTIONNE.md", "CORRECTION_IMMEDIATE.md"
]

deleted = 0
for file in a_supprimer:
    if os.path.exists(file):
        os.remove(file)
        print(f"  🗑️  {file}")
        deleted += 1

print(f"✅ {deleted} fichiers supprimés\n")

# 3. Créer dossier ML
print("📋 3. Création dossier ML...")
if not os.path.exists("analytics/ml_models"):
    os.makedirs("analytics/ml_models")
    with open("analytics/ml_models/.gitkeep", "w") as f:
        f.write("")
    print("✅ analytics/ml_models/ créé\n")

print("=" * 60)
print("🎉 NETTOYAGE TERMINÉ !")
