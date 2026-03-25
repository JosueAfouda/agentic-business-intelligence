import os
import subprocess
import sys
import csv
import json
import argparse
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils.db_discovery import list_databases, list_schemas

# Configuration des chemins
REQUESTS_DIR = Path("requests")
SQL_DIR = Path("sql")
DATAVIZ_DIR = Path("dataviz")
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
        # Using sys.executable to ensure we use the same python interpreter
        full_cmd = [sys.executable, "-m"] + cmd_args
        process = subprocess.run(full_cmd, check=True, capture_output=True, text=True)
        print(process.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERREUR] Une erreur est survenue lors de l'exécution :")
        print(e.stderr)
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

def main(provider_name: str = "gemini"):
    clear_screen()
    print_banner()
    if provider_name != "gemini":
        print(f"LLM provider sélectionné : {provider_name}")
        print()

    # 1. Démarrage
    if not ask_yes_no("Voulez-vous démarrer ?"):
        print("Au revoir !")
        return

    # 2. Database selection
    print("Fetching available databases...")
    databases = list_databases()
    if not databases:
        print("Could not find any databases. Please check your connection settings.")
        return
    
    print("Please select a database:")
    for i, db in enumerate(databases):
        print(f"  {i+1}. {db}")

    selected_db_index = -1
    while selected_db_index < 0 or selected_db_index >= len(databases):
        try:
            choice = input(f"Enter the number of the database (1-{len(databases)}): ")
            selected_db_index = int(choice) - 1
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    selected_database = databases[selected_db_index]
    print(f"You have selected: {selected_database}")

    # 3. Schema selection
    print(f"Fetching available schemas for database '{selected_database}'...")
    schemas = list_schemas(selected_database)
    if not schemas:
        print(f"Could not find any schemas in database '{selected_database}'.")
        return

    print("Please select a schema:")
    for i, schema in enumerate(schemas):
        print(f"  {i+1}. {schema}")

    selected_schema_index = -1
    while selected_schema_index < 0 or selected_schema_index >= len(schemas):
        try:
            choice = input(f"Enter the number of the schema (1-{len(schemas)}): ")
            selected_schema_index = int(choice) - 1
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    selected_schema = schemas[selected_schema_index]
    print(f"You have selected: {selected_schema}")


    # 4. Régénération du schéma
    print(f"Régénération du schéma '{selected_schema}' de la base '{selected_database}'...")
    if run_step(["scripts.schema", "--database", selected_database, "--schema", selected_schema]):
        print(f"Le schéma '{selected_schema}' de la base '{selected_database}' a été régénéré avec succès.")
    else:
        print("Échec de la régénération du schéma. Fin du programme.")
        return

    # 5. Saisie de la question métier
    print("Renseignez votre question métier (soyez le plus clair et explicite possible) :")
    question_text = input("> ").strip()
    while not question_text:
        print("La question ne peut pas être vide.")
        question_text = input("> ").strip()

    # 6. Nom de la question
    print("Donnez un nom à votre question (sans espace, ce nom sera utilisé comme nom de fichier) :")
    question_name = input("> ").strip().replace(" ", "_")
    while not question_name:
        question_name = input("> ").strip().replace(" ", "_")

    # 7. Création de la requête
    REQUESTS_DIR.mkdir(exist_ok=True)
    request_file = REQUESTS_DIR / f"{question_name}.txt"
    
    if request_file.exists():
        if not ask_yes_no(f"Le fichier {request_file.name} existe déjà. Voulez-vous l'écraser ?"):
            print("Action annulée.")
            return

    request_file.write_text(question_text, encoding='utf-8')
    
    # 8. Génération SQL
    print("Génération du code SQL en cours...")
    sql_file = SQL_DIR / f"{question_name}.sql"
    if run_step([
        "scripts.generate_sql",
        "--request",
        str(request_file),
        "--database",
        selected_database,
        "--schema",
        selected_schema,
        "--provider",
        provider_name,
    ]):
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

    # 9. Validation et Exécution
    if not ask_yes_no("Souhaitez-vous valider et exécuter cette requête SQL ?"):
        print("Requête non exécutée. Vous pouvez la retrouver dans le dossier /sql.")
        return

    print("Exécution de l'analyse...")
    if run_step(["scripts.run_analysis", "--sql", str(sql_file), "--database", selected_database, "--schema", selected_schema]):
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

    # 10. Génération Dataviz
    print("Génération du script de visualisation...")
    dataviz_file = DATAVIZ_DIR / f"{question_name}.py"
    if run_step(["scripts.generate_dataviz", "--request", str(request_file), "--provider", provider_name]):
        if dataviz_file.exists():
            print(f"Code dataviz généré : {dataviz_file}")
        else:
            print("[ERREUR] Le fichier dataviz n'a pas été généré.")
            return
    else:
        return

    # 10. Exécution Dataviz
    print("Génération du graphique interactif...")
    if run_step(["scripts.run_dataviz", "--dataviz", str(dataviz_file)]):
        html_path = OUTPUTS_DIR / question_name / f"{question_name}.html"
        if html_path.exists():
            print(f"[OK] Visualisation HTML générée : {html_path}")
        else:
            print("[ERREUR] Le fichier HTML final est introuvable.")
            return
    else:
        return

    # 11. Génération Insights & Actions
    print("Génération des Insights & Actions métiers...")
    if run_step(["scripts.generate_insights_actions", "--request", str(request_file), "--provider", provider_name]):
        md_path = OUTPUTS_DIR / question_name / f"{question_name}.md"
        if md_path.exists():
            print(f"[OK] Insights & Actions générés : {md_path}")
            if ask_yes_no("Souhaitez-vous afficher les Insights & Actions maintenant ?"):
                print("" + "=" * 40)
                print(md_path.read_text(encoding='utf-8'))
                print("=" * 40 + "")
            
            print(f"[OK] Workflow terminé avec succès !")
            print(f"Rapports disponibles dans : {OUTPUTS_DIR / question_name}")
        else:
            print("[ERREUR] Le fichier Markdown d'insights est introuvable.")
    else:
        return

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Agentic BI workflow TUI.")
        parser.add_argument(
            "--provider",
            type=str,
            default="gemini",
            choices=["gemini", "codex"],
            help="LLM provider to use (default: gemini)",
        )
        args = parser.parse_args()
        main(args.provider)
    except KeyboardInterrupt:
        print("\nProgramme interrompu par l'utilisateur. Au revoir !")
        sys.exit(0)
