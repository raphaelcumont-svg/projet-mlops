import mlflow
import mlflow.sklearn
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, f1_score
import numpy as np
import os
import itertools


def run_experiment(experiment_name):
    mlflow.set_experiment(experiment_name)

    # ---- Dataset ----
    data = load_iris()
    X = data.data
    y = data.target

    # ---- Models & Hyperparameters ----
    model_space = {
        "RandomForest": {
            "n_estimators": [50, 100, 150],
            "max_depth": [3, 5, None],
            "random_state": [42],
        },
        "GradientBoosting": {
            "n_estimators": [50, 100],
            "learning_rate": [0.05, 0.1],
            "max_depth": [2, 3],
        },
        "LogisticRegression": {
            "C": [0.1, 1.0, 10],
            "max_iter": [200],
        },
        "SVC": {
            "C": [0.5, 1.0, 2.0],
            "kernel": ["linear", "rbf"],
            "gamma": ["scale"],
        },
    }

    test_sizes = [0.2, 0.3]

    # ---- Loop through all model families ----
    for model_name, hyperparams in model_space.items():

        # Create all combinations of hyperparameters
        keys = hyperparams.keys()
        combinations = list(itertools.product(*hyperparams.values()))

        for combo in combinations:
            params = dict(zip(keys, combo))

            for test_size in test_sizes:
                X_train, X_test, y_train, y_test = train_test_split(
                    X,
                    y,
                    test_size=test_size,
                    random_state=42,
                    stratify=y
                )

                with mlflow.start_run():
                    # ---- Instantiate model based on name ----
                    if model_name == "RandomForest":
                        model = RandomForestClassifier(**params)
                    elif model_name == "GradientBoosting":
                        model = GradientBoostingClassifier(**params)
                    elif model_name == "LogisticRegression":
                        model = LogisticRegression(**params)
                    elif model_name == "SVC":
                        model = SVC(**params)
                    else:
                        continue

                    # ---- Train ----
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)

                    # ---- Metrics ----
                    accuracy = accuracy_score(y_test, y_pred)
                    f1 = f1_score(y_test, y_pred, average="weighted")

                    # ---- Log params ----
                    mlflow.log_param("model_name", model_name)
                    mlflow.log_param("test_size", test_size)
                    for k, v in params.items():
                        mlflow.log_param(k, v)

                    # ---- Log metrics ----
                    mlflow.log_metric("accuracy", accuracy)
                    mlflow.log_metric("f1_weighted", f1)

                    # ---- Log model ----
                    mlflow.sklearn.log_model(model, "model")

                    print(f"Logged model: {model_name} | params={params} | test_size={test_size} | acc={accuracy:.4f}")


def main():
    experiment_name = os.getenv("MLFLOW_EXPERIMENT_NAME", "iris-ml-models")
    run_experiment(experiment_name)


if __name__ == "__main__":
    main()
