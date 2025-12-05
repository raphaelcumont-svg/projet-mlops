#!/bin/bash
set -e

echo "🔧 Chargement des variables d'environnement..."
if [ -f .env ]; then
  set -a
  source .env
  set +a
else
  echo "Fichier .env introuvable, arrêt."
  exit 1
fi

echo "🧨 Destruction de l'infrastructure avec OpenTofu..."
cd tofu
tofu destroy -auto-approve
cd ..

echo "🧹 Nettoyage des fichiers générés..."
if [ -f ansible/inventory.yml ]; then
  rm ansible/inventory.yml
fi

echo "✅ Destruction terminée."