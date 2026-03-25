import argparse
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from llm.factory import generate_with_fallback

SQL_DIR = Path("sql")
PROMPT_TEMPLATE = Path("scripts/prompt_template.txt")

def generate_sql(
    question_file: Path,
    database_name: str,
    schema_name: str = "public",
    provider_name: str = "gemini",
):
    sql_file = SQL_DIR / (question_file.stem + ".sql")
    schema_file = Path(f"schema/{database_name}__{schema_name}_schema.md")

    if not schema_file.exists():
        print(f"Error: Schema file not found at {schema_file}")
        print(f"Please generate the schema first using 'python -m scripts.schema --database {database_name} --schema {schema_name}'")
        sys.exit(1)
    
    # Lecture du prompt template
    prompt = PROMPT_TEMPLATE.read_text()
    prompt = prompt.replace("{{SCHEMA}}", schema_file.read_text())
    prompt = prompt.replace("{{QUESTION}}", question_file.read_text())
    prompt = prompt.replace("{{SQL_PATH}}", str(sql_file))

    # Appel au provider LLM pour générer le SQL
    try:
        result = generate_with_fallback(prompt, provider_name)
    except Exception as exc:
        print("Erreur lors de l'appel au provider LLM :")
        print(exc)
        sys.exit(1)

    sql_file.parent.mkdir(exist_ok=True)
    sql_file.write_text(result.text)
    if result.used_fallback:
        print(f"[WARN] {result.fallback_reason}")
        print("[WARN] Falling back to Gemini to preserve the workflow.")
    print(f"[OK] SQL généré pour {question_file.name}")

def main():
    parser = argparse.ArgumentParser(description="Génère du SQL à partir d'une requête en langage naturel.")
    parser.add_argument("--request", required=True, help="Chemin vers le fichier de requête .txt")
    parser.add_argument("--database", required=True, help="The name of the database.")
    parser.add_argument("--schema", default="public", help="The name of the schema (default: public).")
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

    generate_sql(request_file, args.database, args.schema, args.provider)

if __name__ == "__main__":
    main()
