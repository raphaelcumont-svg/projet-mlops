#!/bin/bash
set -e

PROJECT_DIR=$(pwd)

echo "🐍 Vérification/activation de l'environnement virtuel..."

if [ ! -d "venv" ]; then
  echo "🔧 Aucun venv détecté, création..."
  sudo apt install python3.12-venv -y
  python3 -m venv venv
  source venv/bin/activate
  echo "📦 Installation des dépendances MLflow..."
  pip install -r mlflow/requirements.txt
else
  # Si venv existe, on l'active
  echo "🔁 Activation du venv existant..."
  source venv/bin/activate
fi

echo "🔧 Chargement des variables d'environnement..."
if [ -f .env ]; then
  set -a
  source .env
  set +a
else
  echo "❌ ERREUR : fichier .env introuvable, arrêt."
  exit 1
fi

echo "📈 Entraînement du modèle avec MLflow..."
cd mlflow
python3 train.py
python3 select_best.py
cd $PROJECT_DIR

echo "🚀 Déploiement de l'infrastructure avec OpenTofu..."
cd tofu
tofu init -input=false
tofu apply -auto-approve
cd $PROJECT_DIR

echo "🧾 Génération de l'inventaire Ansible..."
python3 generate_inventory.py

echo "🐧 Déploiement de l'API avec Ansible..."
cd ansible
ansible-playbook -i inventory.yml playbook-api.yml

echo "📊 Déploiement du monitoring (Prometheus + Grafana)..."
ansible-playbook -i inventory.yml playbook-monitoring.yml
cd $PROJECT_DIR

echo "🎉 Déploiement terminé avec succès !"
echo "🌍 URL API : $(cd tofu && tofu output -raw api_url)"
echo "📊 URL Grafana : $(cd tofu && tofu output -raw grafana_url)"
