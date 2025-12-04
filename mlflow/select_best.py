import mlflow
from mlflow.tracking import MlflowClient
from mlflow.artifacts import download_artifacts
from pathlib import Path
import shutil
import os


def get_best_run(experiment_name):
    client = MlflowClient()
    experiment = client.get_experiment_by_name(experiment_name)
    if experiment is None:
        raise ValueError(f"Experiment '{experiment_name}' not found")

    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["metrics.accuracy DESC"],
        max_results=1
    )

    if len(runs) == 0:
        raise ValueError("No runs found for this experiment")

    return runs[0]


def export_best_model(best_run, export_dir):
    model_uri = f"runs:/{best_run.info.run_id}/model"
    if export_dir.exists():
        shutil.rmtree(export_dir)
    tmp_dir = download_artifacts(model_uri)
    shutil.copytree(tmp_dir, export_dir)


def main():
    experiment_name = os.getenv("MLFLOW_EXPERIMENT_NAME", "iris-ml-models")
    project_root = Path(__file__).resolve().parent.parent
    export_dir = project_root / "api" / "model"

    best_run = get_best_run(experiment_name)

    print("Best run ID:", best_run.info.run_id)
    print("Best model name:", best_run.data.params.get("model_name"))
    print("Best accuracy:", best_run.data.metrics.get("accuracy"))
    print("Best params:", best_run.data.params)

    export_best_model(best_run, export_dir)


if __name__ == "__main__":
    main()
