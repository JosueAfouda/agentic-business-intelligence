import csv
import json
from pathlib import Path
from utils.db_utils import run_query

SQL_DIR = Path("sql")
OUTPUTS_DIR = Path("outputs")

def run():
    # Parcours tous les fichiers .sql
    for sql_file in SQL_DIR.glob("*.sql"):
        question_name = sql_file.stem
        out_dir = OUTPUTS_DIR / question_name
        csv_path = out_dir / f"{question_name}.csv"

        # Skip si le résultat existe déjà
        if csv_path.exists():
            print(f"[SKIP] {csv_path} existe déjà, pas d'exécution")
            continue

        # Lecture et nettoyage du SQL
        #sql_content = clean_sql(sql_file.read_text())

        # Exécution de la requête
        columns, rows = run_query(sql_file.read_text()) #sql_content si nettoyage

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

if __name__ == "__main__":
    run()
