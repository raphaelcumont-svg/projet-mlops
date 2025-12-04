import streamlit as st
import subprocess
from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parent


def run_command(cmd, cwd=None):
    result = subprocess.run(
        cmd,
        cwd=cwd,
        shell=True,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr


def action_train_and_select():
    mlflow_dir = PROJECT_ROOT / "mlflow"
    code1, out1, err1 = run_command("python train.py", cwd=mlflow_dir)
    code2, out2, err2 = run_command("python select_best.py", cwd=mlflow_dir)
    return (code1, out1, err1), (code2, out2, err2)


def action_tofu_apply():
    tofu_dir = PROJECT_ROOT / "tofu"
    code1, out1, err1 = run_command("tofu init", cwd=tofu_dir)
    code2, out2, err2 = run_command("tofu apply -auto-approve", cwd=tofu_dir)
    return (code1, out1, err1), (code2, out2, err2)


def action_ansible():
    ansible_dir = PROJECT_ROOT / "ansible"
    code, out, err = run_command(
        "ansible-playbook -i inventory.yml playbook-api.yml playbook-monitoring.yml",
        cwd=ansible_dir
    )
    return code, out, err


def action_tofu_destroy():
    tofu_dir = PROJECT_ROOT / "tofu"
    code, out, err = run_command("tofu destroy -auto-approve", cwd=tofu_dir)
    return code, out, err


def get_urls():
    tofu_dir = PROJECT_ROOT / "tofu"
    api_url = None
    grafana_url = None

    code_api, out_api, _ = run_command("tofu output -raw api_url", cwd=tofu_dir)
    if code_api == 0:
        api_url = out_api.strip()

    code_graf, out_graf, _ = run_command("tofu output -raw grafana_url", cwd=tofu_dir)
    if code_graf == 0:
        grafana_url = out_graf.strip()

    return api_url, grafana_url


def action_full_deploy():
    ml_results = action_train_and_select()
    tofu_results = action_tofu_apply()
    ansible_result = action_ansible()
    api_url, grafana_url = get_urls()
    return ml_results, tofu_results, ansible_result, api_url, grafana_url


st.set_page_config(page_title="Projet MLOps", layout="wide")

st.title("🚀 Interface de pilotage – Projet MLOps")

st.sidebar.header("Actions")
mode = st.sidebar.radio(
    "Choisis une action",
    [
        "Entraîner modèles + sélectionner le meilleur",
        "Provisionner l'infrastructure (OpenTofu)",
        "Configurer les instances (Ansible)",
        "Déploiement complet",
        "Afficher les URLs (API / Grafana)",
        "Détruire l'infrastructure"
    ]
)

st.write("Racine du projet :", f"`{PROJECT_ROOT}`")

if mode == "Entraîner modèles + sélectionner le meilleur":
    st.subheader("📈 Entraînement + sélection du meilleur modèle")
    if st.button("Lancer l'entraînement MLflow"):
        r1, r2 = action_train_and_select()
        code1, out1, err1 = r1
        code2, out2, err2 = r2

        st.write("Résultat `train.py` (code retour :", code1, ")")
        st.code(out1 or "(stdout vide)")
        if err1:
            st.error(err1)

        st.write("Résultat `select_best.py` (code retour :", code2, ")")
        st.code(out2 or "(stdout vide)")
        if err2:
            st.error(err2)

elif mode == "Provisionner l'infrastructure (OpenTofu)":
    st.subheader("🏗️ Provisionnement OpenTofu")
    if st.button("Lancer tofu init + apply"):
        r1, r2 = action_tofu_apply()
        code1, out1, err1 = r1
        code2, out2, err2 = r2

        st.write("Résultat `tofu init` (code retour :", code1, ")")
        st.code(out1 or "(stdout vide)")
        if err1:
            st.error(err1)

        st.write("Résultat `tofu apply` (code retour :", code2, ")")
        st.code(out2 or "(stdout vide)")
        if err2:
            st.error(err2)

elif mode == "Configurer les instances (Ansible)":
    st.subheader("⚙️ Configuration Ansible")
    if st.button("Lancer ansible-playbook"):
        code, out, err = action_ansible()
        st.write("Résultat Ansible (code retour :", code, ")")
        st.code(out or "(stdout vide)")
        if err:
            st.error(err)

elif mode == "Déploiement complet":
    st.subheader("🚀 Déploiement complet du pipeline")
    if st.button("Lancer le déploiement complet"):
        ml_results, tofu_results, ansible_result, api_url, grafana_url = action_full_deploy()

        r1, r2 = ml_results
        code1, out1, err1 = r1
        code2, out2, err2 = r2

        st.markdown("### Étape 1 – MLflow (train + select)")
        st.write("`train.py` (code retour :", code1, ")")
        st.code(out1 or "(stdout vide)")
        if err1:
            st.error(err1)

        st.write("`select_best.py` (code retour :", code2, ")")
        st.code(out2 or "(stdout vide)")
        if err2:
            st.error(err2)

        r_to1, r_to2 = tofu_results
        code_t1, out_t1, err_t1 = r_to1
        code_t2, out_t2, err_t2 = r_to2

        st.markdown("### Étape 2 – OpenTofu")
        st.write("`tofu init` (code retour :", code_t1, ")")
        st.code(out_t1 or "(stdout vide)")
        if err_t1:
            st.error(err_t1)

        st.write("`tofu apply` (code retour :", code_t2, ")")
        st.code(out_t2 or "(stdout vide)")
        if err_t2:
            st.error(err_t2)

        code_ans, out_ans, err_ans = ansible_result

        st.markdown("### Étape 3 – Ansible")
        st.write("Ansible (code retour :", code_ans, ")")
        st.code(out_ans or "(stdout vide)")
        if err_ans:
            st.error(err_ans)

        st.markdown("### Étape 4 – URLs")
        st.write("API URL :", api_url or "Non disponible")
        st.write("Grafana URL :", grafana_url or "Non disponible")

elif mode == "Afficher les URLs (API / Grafana)":
    st.subheader("🌐 URLs de l'API et de Grafana")
    if st.button("Récupérer les URLs depuis OpenTofu"):
        api_url, grafana_url = get_urls()
        st.write("API URL :", api_url or "Non disponible")
        st.write("Grafana URL :", grafana_url or "Non disponible")

elif mode == "Détruire l'infrastructure":
    st.subheader("💣 Destruction de l'infrastructure")
    if st.button("Lancer tofu destroy"):
        code, out, err = action_tofu_destroy()
        st.write("Résultat `tofu destroy` (code retour :", code, ")")
        st.code(out or "(stdout vide)")
        if err:
            st.error(err)
