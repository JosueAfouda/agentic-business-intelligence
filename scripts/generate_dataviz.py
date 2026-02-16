import subprocess
import csv
import json
import argparse
import sys
from pathlib import Path

SQL_DIR = Path("sql")
OUTPUTS_DIR = Path("outputs")
DATAVIZ_DIR = Path("dataviz")
PROMPT_TEMPLATE = Path("scripts/prompt_template_dataviz.txt")

def sanitize_python_output(text: str) -> str:
    """
    Supprime toute ligne avant le premier import/from/def
    afin de garantir un fichier Python valide.
    """
    lines = text.splitlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(("import ", "from ", "def ", "class ")):
            return "\n".join(lines[i:])
    return text

def preview_csv(csv_path: Path, limit: int = 5):
    """Retourne un aperçu texte des premières lignes du CSV."""
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if not header:
            return "", [], 0

        for _ in range(limit):
            try:
                rows.append(next(reader))
            except StopIteration:
                break

    return header, rows, sum(1 for _ in open(csv_path, encoding="utf-8")) - 1

def generate_dataviz(question_file: Path):
    question_name = question_file.stem

    sql_file = SQL_DIR / f"{question_name}.sql"
    csv_file = OUTPUTS_DIR / question_name / f"{question_name}.csv"
    metadata_file = OUTPUTS_DIR / question_name / "metadata.json"
    dataviz_file = DATAVIZ_DIR / f"{question_name}.py"
    output_html = OUTPUTS_DIR / question_name / f"{question_name}.html"

    if not (sql_file.exists() and csv_file.exists() and metadata_file.exists()):
        print(f"Erreur : Données manquantes pour {question_name} (SQL, CSV ou Metadata absent)")
        sys.exit(1)

    # Lecture des fichiers
    question_text = question_file.read_text(encoding="utf-8")
    sql_code = sql_file.read_text(encoding="utf-8")
    metadata = json.loads(metadata_file.read_text(encoding="utf-8"))

    columns, rows_preview, row_count = preview_csv(csv_file)
    csv_preview_text = "\n".join([", ".join(r) for r in rows_preview])

    # Construction du prompt
    prompt = PROMPT_TEMPLATE.read_text(encoding="utf-8")
    prompt = prompt.replace("{{ORIGINAL_QUESTION}}", question_text)
    prompt = prompt.replace("{{SQL_CODE}}", sql_code)
    prompt = prompt.replace("{{COLUMNS}}", ", ".join(columns))
    prompt = prompt.replace("{{CSV_PREVIEW}}", csv_preview_text)
    prompt = prompt.replace("{{ROW_COUNT}}", str(row_count))
    prompt = prompt.replace("{{CSV_PATH}}", str(csv_file))
    prompt = prompt.replace("{{OUTPUT_HTML_PATH}}", str(output_html))

    # Appel à Gemini CLI
    result = subprocess.run(
        ["gemini", "run"],
        input=prompt,
        text=True,
        capture_output=True
    )

    DATAVIZ_DIR.mkdir(exist_ok=True)
    clean_code = sanitize_python_output(result.stdout)
    dataviz_file.write_text(clean_code, encoding="utf-8")

    print(f"[OK] Code dataviz généré pour {question_name}")

def main():
    parser = argparse.ArgumentParser(description="Génère un script de visualisation de données.")
    parser.add_argument("--request", required=True, help="Chemin vers le fichier de requête .txt")
    args = parser.parse_args()

    request_file = Path(args.request)
    if not request_file.exists():
        print(f"Erreur : Le fichier {request_file} n'existe pas.")
        sys.exit(1)

    generate_dataviz(request_file)

if __name__ == "__main__":
    main()
