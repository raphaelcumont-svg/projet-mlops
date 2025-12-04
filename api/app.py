import time
import json
import pandas as pd
from flask import Flask, request, jsonify
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

# Importation des modules locaux
from model_loader import load_mlflow_model
from prometheus_instrumentation import (
    start_prometheus_server,
    REQUEST_COUNT,
    REQUEST_LATENCY,
    MODEL_AVAILABLE
)

# --- Initialisation Globale ---

# 1. Charger le modèle
model = load_mlflow_model()

# 2. Démarrer le serveur Prometheus
start_prometheus_server()

# 3. Mettre à jour la métrique de disponibilité du modèle (1 si chargé, 0 sinon)
MODEL_AVAILABLE.inc(1 if model else 0)

# --- Flask App ---
app = Flask(__name__)

# Point de terminaison de prédiction
@app.route('/predict', methods=['POST'])
@REQUEST_LATENCY.time()  # Démarre l'enregistrement de la latence
def predict():
    
    # Incrémenter le compteur de requêtes
    REQUEST_COUNT.labels(method='post', endpoint='/predict').inc()

    # Vérification de la disponibilité du modèle
    if model is None:
        # La métrique de latence est enregistrée par le décorateur @REQUEST_LATENCY.time()
        return jsonify({"error": "Model not loaded. Service Unavailable."}), 503

    try:
        # 1. Récupération et conversion des données
        data = request.get_json(force=True)
        # S'assurer que les données sont dans le format attendu (e.g., liste de features)
        features = data.get('features')
        df = pd.DataFrame([features]) 

        # 2. Prédiction
        prediction = model.predict(df)
        
        # Le temps de latence est automatiquement observé par le décorateur .time()

        return jsonify({
            "prediction": prediction.tolist(), 
            "status": "success"
        })

    except Exception as e:
        # En cas d'erreur dans le traitement des données
        return jsonify({"error": str(e), "message": "Input data format error"}), 400

# Point de terminaison de santé
@app.route('/health', methods=['GET'])
def health():
    # Utilisé par Ansible/load-balancer pour vérifier si le conteneur est en vie
    REQUEST_COUNT.labels(method='get', endpoint='/health').inc()
    status = "Model Loaded" if model else "No Model Loaded"
    return jsonify({"status": "OK", "model_state": status}), 200

# Point de terminaison pour les métriques, scruté par Prometheus
@app.route('/metrics', methods=['GET'])
def metrics():
    # Retourne le contenu des métriques au format texte pour Prometheus
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}


# Le Gunicorn (défini dans le Dockerfile) appellera l'objet 'app' pour lancer le serveur.