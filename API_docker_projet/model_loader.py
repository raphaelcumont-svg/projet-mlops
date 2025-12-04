import os
import mlflow.pyfunc

# Configuration des variables d'environnement (définies dans le Dockerfile ou par Ansible)
MODEL_NAME = os.environ.get("MODEL_NAME", "iris_classifier")
MODEL_STAGE = os.environ.get("MODEL_STAGE", "Production")
MLFLOW_TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI")

def load_mlflow_model():
    """
    Charge la version 'Production' du modèle depuis le Model Registry MLflow.
    """
    model = None
    if not MLFLOW_TRACKING_URI:
        print("Erreur: MLFLOW_TRACKING_URI n'est pas défini. Impossible de charger le modèle.")
        return None

    try:
        # 1. Définir le serveur de tracking
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        
        # 2. Construire l'URI de chargement
        MODEL_URI = f"models:/{MODEL_NAME}/{MODEL_STAGE}"
        
        # 3. Charger le modèle MLflow
        model = mlflow.pyfunc.load_model(MODEL_URI)
        print(f"✅ Modèle chargé: {MODEL_NAME} - Stage: {MODEL_STAGE}")
        
    except Exception as e:
        print(f"❌ Erreur critique lors du chargement du modèle MLflow ({MODEL_URI}): {e}")
        
    return model