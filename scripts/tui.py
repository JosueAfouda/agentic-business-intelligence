import os
import subprocess
import sys
import csv
import json
from pathlib import Path

# Configuration des chemins
REQUESTS_DIR = Path("requests")
SQL_DIR = Path("sql")
DATAVIZ_DIR = Path("dataviz")
SCHEMA_FILE = Path("schema/dvdrental_schema.md")
OUTPUTS_DIR = Path("outputs")

def clear_screen():
    """Efface le terminal pour une meilleure lisibilité."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Affiche le bandeau de bienvenue."""
    print("=" * 60)
    print("      BIENVENUE DANS L'INTERFACE AGENTIC BI WORKFLOW")
    print("=" * 60)
    print()

def ask_yes_no(prompt):
    """Gère les questions Oui/Non de manière robuste."""
    while True:
        choice = input(f"{prompt} (Oui / Non) : ").strip().lower()
        if choice in ['oui', 'o', 'yes', 'y']:
            return True
        if choice in ['non', 'n', 'no']:
            return False
        print("Veuillez répondre par 'Oui' ou 'Non'.")

def run_step(cmd_args):
    """Exécute une commande de workflow et gère les erreurs."""
    try:
        subprocess.run(cmd_args, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERREUR] Une erreur est survenue lors de l'exécution :")
        print(e.stderr.decode())
        return False

def display_csv_table(csv_path, limit=5):
    """Affiche les premières lignes d'un CSV sous forme de tableau simple."""
    if not csv_path.exists():
        print(f"[ERREUR] Fichier CSV introuvable : {csv_path}")
        return

    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if not header:
                print("Le fichier CSV est vide.")
                return

            rows = []
            for _ in range(limit):
                try:
                    rows.append(next(reader))
                except StopIteration:
                    break

            all_data = [header] + rows
            widths = [max(len(str(item)) for item in col) for col in zip(*all_data)]
            
            separator = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
            
            print(separator)
            print("| " + " | ".join(str(item).ljust(widths[i]) for i, item in enumerate(header)) + " |")
            print(separator)
            for row in rows:
                print("| " + " | ".join(str(item).ljust(widths[i]) for i, item in enumerate(row)) + " |")
            print(separator)

    except Exception as e:
        print(f"Erreur lors de l'affichage du tableau : {e}")

def main():
    clear_screen()
    print_banner()

    # 1. Démarrage
    if not ask_yes_no("Voulez-vous démarrer ?"):
        print("Au revoir !")
        return

    # 2. Régénération du schéma
    if SCHEMA_FILE.exists():
        SCHEMA_FILE.unlink()
    
    print("Régénération du schéma de la base de données...")
    if run_step([sys.executable, "-m", "scripts.schema"]):
        print("Le schéma de la base dvdrental a été régénéré avec succès.")
    else:
        print("Échec de la régénération du schéma. Fin du programme.")
        return

    # 3. Saisie de la question métier
    print("Renseignez votre question métier (soyez le plus clair et explicite possible) :")
    question_text = input("> ").strip()
    while not question_text:
        print("La question ne peut pas être vide.")
        question_text = input("> ").strip()

    # 4. Nom de la question
    print("Donnez un nom à votre question (sans espace, ce nom sera utilisé comme nom de fichier) :")
    question_name = input("> ").strip().replace(" ", "_")
    while not question_name:
        question_name = input("> ").strip().replace(" ", "_")

    # 5. Création de la requête
    REQUESTS_DIR.mkdir(exist_ok=True)
    request_file = REQUESTS_DIR / f"{question_name}.txt"
    
    if request_file.exists():
        if not ask_yes_no(f"Le fichier {request_file.name} existe déjà. Voulez-vous l'écraser ?"):
            print("Action annulée.")
            return

    request_file.write_text(question_text, encoding='utf-8')
    
    # 6. Génération SQL
    print("Génération du code SQL en cours...")
    sql_file = SQL_DIR / f"{question_name}.sql"
    if run_step([sys.executable, "scripts/generate_sql.py", "--request", str(request_file)]):
        if sql_file.exists():
            print(f"Code SQL généré avec succès.")
            print(f"Chemin : {sql_file}")
            print("-" * 40)
            print(sql_file.read_text(encoding='utf-8'))
            print("-" * 40)
        else:
            print("[ERREUR] Le script de génération a réussi mais le fichier SQL est introuvable.")
            return
    else:
        return

    # 7. Validation et Exécution
    if not ask_yes_no("Souhaitez-vous valider et exécuter cette requête SQL ?"):
        print("Requête non exécutée. Vous pouvez la retrouver dans le dossier /sql.")
        return

    print("Exécution de l'analyse...")
    if run_step([sys.executable, "-m", "scripts.run_analysis", "--sql", str(sql_file)]):
        out_dir = OUTPUTS_DIR / question_name
        csv_path = out_dir / f"{question_name}.csv"
        meta_path = out_dir / "metadata.json"

        if csv_path.exists() and meta_path.exists():
            print(f"Analyse terminée.")
            print("Aperçu des résultats (5 premières lignes) :")
            display_csv_table(csv_path)

            print("Contenu du fichier metadata.json :")
            print(meta_path.read_text(encoding='utf-8'))
        else:
            print("[ERREUR] Les fichiers de sortie n'ont pas été générés.")
            return
    else:
        print("[ERREUR] Échec de l'exécution de l'analyse.")
        return

    # 8. Génération Dataviz
    print("Génération du script de visualisation...")
    if run_step([sys.executable, "-m", "scripts.generate_dataviz", "--request", str(request_file)]):
        dataviz_file = DATAVIZ_DIR / f"{question_name}.py"
        if dataviz_file.exists():
            print(f"Code dataviz généré : {dataviz_file}")
        else:
            print("[ERREUR] Le fichier dataviz n'a pas été généré.")
            return
    else:
        return

    # 9. Exécution Dataviz
    print("Génération du graphique interactif...")
    if run_step([sys.executable, "-m", "scripts.run_dataviz", "--dataviz", str(dataviz_file)]):
        html_path = OUTPUTS_DIR / question_name / f"{question_name}.html"
        if html_path.exists():
            print(f"\n[OK] Visualisation terminée avec succès !")
            print(f"Le rapport HTML est disponible ici : {html_path}")
            print("Vous pouvez l'ouvrir manuellement dans votre navigateur préféré.")
        else:
            print("[ERREUR] Le fichier HTML final est introuvable.")
    else:
        return

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgramme interrompu par l'utilisateur. Au revoir !")
        sys.exit(0)
