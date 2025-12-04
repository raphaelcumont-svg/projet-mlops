from prometheus_client import start_http_server, Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Port pour le serveur de métriques (doit correspondre à l'EXPOSE 8000 du Dockerfile)
PROMETHEUS_PORT = 8000 

# --- Définition des Métriques Globales ---

# 1. Compteur de requêtes totales (par méthode et endpoint)
REQUEST_COUNT = Counter(
    'http_requests_total', 
    'Total du nombre de requêtes HTTP', 
    ['method', 'endpoint']
)

# 2. Histogramme pour la latence des requêtes (par méthode et endpoint)
REQUEST_LATENCY = Histogram(
    'http_request_latency_seconds', 
    'Latence des requêtes HTTP (en secondes)', 
    ['method', 'endpoint']
)

# 3. Jauge pour la disponibilité du modèle (utilisée dans app.py)
MODEL_AVAILABLE = Counter(
    'model_availability', 
    'Modèle ML en production disponible (1) ou non (0)'
)


def start_prometheus_server():
    """
    Démarre le serveur HTTP sur le port 8000 pour que Prometheus puisse collecter les métriques.
    """
    try:
        start_http_server(PROMETHEUS_PORT)
        print(f"✅ Serveur de métriques Prometheus démarré sur le port {PROMETHEUS_PORT}")
    except Exception as e:
        print(f"❌ Erreur lors du démarrage du serveur Prometheus: {e}")

# Le reste de la logique (generate_latest, CONTENT_TYPE_LATEST) sera utilisé dans app.py
# pour l'endpoint '/metrics'.