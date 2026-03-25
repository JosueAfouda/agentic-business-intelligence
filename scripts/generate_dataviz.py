import ast
import csv
import json
import argparse
import re
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from llm.factory import generate_with_fallback

SQL_DIR = Path("sql")
OUTPUTS_DIR = Path("outputs")
DATAVIZ_DIR = Path("dataviz")
PROMPT_TEMPLATE = Path("scripts/prompt_template_dataviz.txt")

def sanitize_python_output(text: str) -> str:
    """
    Extrait le bloc Python le plus probable depuis la sortie du provider.
    """
    if "```" in text:
        fenced_blocks = re.findall(r"```(?:python)?\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
        if fenced_blocks:
            return fenced_blocks[0].strip()

    lines = text.splitlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(("import ", "from ", "def ", "class ")):
            return "\n".join(lines[i:])
    return text


def validate_python_output(text: str) -> None:
    """Refuse d'écrire un fichier si la sortie n'est pas du Python valide."""
    if not text.strip():
        raise ValueError("Le provider a retourné une sortie vide pour la dataviz.")
    if "```" in text:
        raise ValueError("Le provider a retourné du markdown au lieu d'un script Python brut.")

    try:
        ast.parse(text)
    except SyntaxError as exc:
        raise ValueError(f"Le provider a retourné un script Python invalide: {exc}") from exc

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

def generate_dataviz(question_file: Path, provider_name: str = "gemini"):
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
    csv_preview_text = "\n".join([", ".join(r) for r in rows_preview]) or "(no preview rows)"

    # Construction du prompt
    prompt = PROMPT_TEMPLATE.read_text(encoding="utf-8")
    template_values = {
        "{original_business_question}": question_text.strip(),
        "{question_that_sql_result_can_answer}": metadata.get(
            "question_that_sql_result_can_answer",
            question_text.strip(),
        ),
        "{sql_code}": sql_code,
        "{columns_string}": ", ".join(columns),
        "{dataframe_preview_len}": str(len(rows_preview)),
        "{dataframe_head}": csv_preview_text,
        "{dataframe_len}": str(row_count),
        "{csv_path}": str(csv_file),
        "{output_html_path}": str(output_html),
    }

    for placeholder, value in template_values.items():
        prompt = prompt.replace(placeholder, value)

    unresolved = sorted(set(re.findall(r"\{[a-z_][a-z0-9_]*\}", prompt)))
    if unresolved:
        raise ValueError(
            f"Unresolved dataviz prompt placeholders: {', '.join(unresolved)}"
        )

    # Appel au provider LLM
    try:
        result = generate_with_fallback(prompt, provider_name)
    except Exception as exc:
        print("Erreur lors de l'appel au provider LLM :")
        print(exc)
        sys.exit(1)

    DATAVIZ_DIR.mkdir(exist_ok=True)
    clean_code = sanitize_python_output(result.text)
    validate_python_output(clean_code)
    dataviz_file.write_text(clean_code, encoding="utf-8")
    if result.used_fallback:
        print(f"[WARN] {result.fallback_reason}")
        print("[WARN] Falling back to Gemini to preserve the workflow.")

    print(f"[OK] Code dataviz généré pour {question_name}")

def main():
    parser = argparse.ArgumentParser(description="Génère un script de visualisation de données.")
    parser.add_argument("--request", required=True, help="Chemin vers le fichier de requête .txt")
    parser.add_argument(
        "--provider",
        type=str,
        default="gemini",
        choices=["gemini", "codex"],
        help="LLM provider to use (default: gemini)",
    )
    args = parser.parse_args()

    request_file = Path(args.request)
    if not request_file.exists():
        print(f"Erreur : Le fichier {request_file} n'existe pas.")
        sys.exit(1)

    generate_dataviz(request_file, args.provider)

if __name__ == "__main__":
    main()
