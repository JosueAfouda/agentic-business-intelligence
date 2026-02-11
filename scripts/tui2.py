import os
import subprocess
import sys
import csv
from pathlib import Path

# Configuration des chemins (alignée sur les scripts existants)
REQUESTS_DIR = Path("requests")
SQL_DIR = Path("sql")
SCHEMA_FILE = Path("schema/dvdrental_schema.md")
OUTPUTS_DIR = Path("outputs")
DATAVIZ_DIR = Path("dataviz")


def clear_screen():
    """Clear the terminal for better readability."""
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    """Display welcome banner."""
    print("=" * 60)
    print("      BIENVENUE DANS L'INTERFACE AGENTIC BI WORKFLOW")
    print("=" * 60)
    print()


def ask_yes_no(prompt):
    """Robust Yes/No prompt."""
    while True:
        choice = input(f"{prompt} (Oui / Non) : ").strip().lower()
        if choice in ["oui", "o", "yes", "y"]:
            return True
        if choice in ["non", "n", "no"]:
            return False
        print("Veuillez répondre par 'Oui' ou 'Non'.")


def run_script(module_name):
    """Run a Python script as a module."""
    try:
        subprocess.run(
            [sys.executable, "-m", f"scripts.{module_name}"],
            check=True,
            capture_output=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERREUR] Une erreur est survenue lors de l'exécution de {module_name} :")
        print(e.stderr.decode())
        return False


def display_csv_table(csv_path, limit=5):
    """Display first rows of a CSV file as a simple table."""
    if not csv_path.exists():
        print(f"[ERREUR] Fichier CSV introuvable : {csv_path}")
        return

    try:
        with open(csv_path, mode="r", encoding="utf-8") as f:
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
            print(
                "| "
                + " | ".join(
                    str(item).ljust(widths[i]) for i, item in enumerate(header)
                )
                + " |"
            )
            print(separator)

            for row in rows:
                print(
                    "| "
                    + " | ".join(
                        str(item).ljust(widths[i]) for i, item in enumerate(row)
                    )
                    + " |"
                )

            print(separator)

    except Exception as e:
        print(f"Erreur lors de l'affichage du tableau : {e}")


def main():
    clear_screen()
    print_banner()

    # 1. Start
    if not ask_yes_no("Voulez-vous démarrer ?"):
        print("Au revoir !")
        return

    # 2. Regenerate schema
    if SCHEMA_FILE.exists():
        SCHEMA_FILE.unlink()

    print("Régénération du schéma de la base de données...")
    if not run_script("schema"):
        print("Échec de la régénération du schéma. Fin du programme.")
        return

    # 3. Business question
    print("Renseignez votre question métier (soyez le plus clair et explicite possible) :")
    question_text = input("> ").strip()
    while not question_text:
        print("La question ne peut pas être vide.")
        question_text = input("> ").strip()

    # 4. Question name
    print("Donnez un nom à votre question (sans espace) :")
    question_name = input("> ").strip().replace(" ", "_")
    while not question_name:
        question_name = input("> ").strip().replace(" ", "_")

    # 5. Save request
    REQUESTS_DIR.mkdir(exist_ok=True)
    request_file = REQUESTS_DIR / f"{question_name}.txt"

    if request_file.exists():
        if not ask_yes_no(f"{request_file.name} existe déjà. Voulez-vous l'écraser ?"):
            print("Action annulée.")
            return

    request_file.write_text(question_text, encoding="utf-8")

    # 6. Generate SQL
    print("Génération du code SQL en cours...")
    if not run_script("generate_sql"):
        return

    sql_file = SQL_DIR / f"{question_name}.sql"
    if not sql_file.exists():
        print("[ERREUR] Fichier SQL introuvable.")
        return

    print("Code SQL généré avec succès :")
    print("-" * 40)
    print(sql_file.read_text(encoding="utf-8"))
    print("-" * 40)

    # 7. Execute analysis
    if not ask_yes_no("Souhaitez-vous valider et exécuter cette requête SQL ?"):
        print("Requête non exécutée.")
        return

    print("Exécution de l'analyse...")
    if not run_script("run_analysis"):
        print("[ERREUR] Échec de l'exécution de l'analyse.")
        return

    out_dir = OUTPUTS_DIR / question_name
    csv_path = out_dir / f"{question_name}.csv"
    meta_path = out_dir / "metadata.json"

    if not (csv_path.exists() and meta_path.exists()):
        print("[ERREUR] Fichiers de sortie manquants.")
        return

    print("Analyse terminée.")
    print(f"CSV : {csv_path}")
    print(f"Metadata : {meta_path}")

    print("\nAperçu des résultats :")
    display_csv_table(csv_path)

    print("\nContenu du fichier metadata.json :")
    print(meta_path.read_text(encoding="utf-8"))

    # 8. Generate dataviz
    print("\nGénération de la visualisation...")
    if not run_script("generate_dataviz"):
        print("[ERREUR] Échec génération dataviz.")
        return

    dataviz_file = DATAVIZ_DIR / f"{question_name}.py"
    if dataviz_file.exists():
        print(f"[OK] Code dataviz généré : {dataviz_file}")

    # 9. Run dataviz
    print("Exécution du graphique...")
    if not run_script("run_dataviz"):
        print("[ERREUR] Échec exécution dataviz.")
        return

    html_path = out_dir / f"{question_name}.html"
    if html_path.exists():
        print(f"[OK] Visualisation HTML générée : {html_path}")
        if ask_yes_no("Souhaitez-vous voir comment ouvrir le graphique ?"):
            print(f"file://{html_path.absolute()}")
    else:
        print("[ERREUR] Fichier HTML introuvable.")

    print("\nWorkflow terminé avec succès.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgramme interrompu par l'utilisateur. Au revoir !")
        sys.exit(0)
