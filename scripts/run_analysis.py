import csv
import json
import argparse
import sys
from pathlib import Path
from utils.db_utils import run_query

OUTPUTS_DIR = Path("outputs")

def execute_analysis(sql_file: Path):
    question_name = sql_file.stem
    out_dir = OUTPUTS_DIR / question_name
    csv_path = out_dir / f"{question_name}.csv"

    # Exécution de la requête
    columns, rows = run_query(sql_file.read_text())

    # Création du dossier de sortie si nécessaire
    out_dir.mkdir(parents=True, exist_ok=True)

    # Écriture du CSV
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)

    # Écriture des métadonnées
    metadata = {
        "question": question_name,
        "rows_returned": len(rows),
        "columns": columns,
        "sql_file": str(sql_file)
    }
    (out_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

    print(f"[OK] Résultat généré pour {question_name}")

def main():
    parser = argparse.ArgumentParser(description="Exécute une requête SQL et exporte les résultats.")
    parser.add_argument("--sql", required=True, help="Chemin vers le fichier SQL à exécuter")
    args = parser.parse_args()

    sql_file = Path(args.sql)
    if not sql_file.exists():
        print(f"Erreur : Le fichier {sql_file} n'existe pas.")
        sys.exit(1)

    execute_analysis(sql_file)

if __name__ == "__main__":
    main()
