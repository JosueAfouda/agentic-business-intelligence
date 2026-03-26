import csv
import json
import argparse
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from llm.factory import generate_with_fallback

OUTPUTS_DIR = Path("outputs")
PROMPT_TEMPLATE = Path("scripts/prompt_template_insights.txt")


def preview_csv(csv_path: Path, limit: int = 10):
    """Return header, preview rows and total row count."""
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if not header:
            return [], [], 0

        for _ in range(limit):
            try:
                rows.append(next(reader))
            except StopIteration:
                break

    total_rows = sum(1 for _ in open(csv_path, encoding="utf-8")) - 1
    return header, rows, total_rows


def generate_insights_actions(question_file: Path, provider_name: str = "gemini"):
    question_name = question_file.stem

    output_dir = OUTPUTS_DIR / question_name
    csv_file = output_dir / f"{question_name}.csv"
    metadata_file = output_dir / "metadata.json"
    output_md = output_dir / f"{question_name}.md"

    if not csv_file.exists():
        print(f"Erreur : CSV introuvable pour {question_name}")
        sys.exit(1)

    if not metadata_file.exists():
        print(f"Erreur : metadata.json introuvable pour {question_name}")
        sys.exit(1)

    if not PROMPT_TEMPLATE.exists():
        print("Erreur : prompt_template_insights.txt introuvable.")
        sys.exit(1)

    # Load inputs
    question_text = question_file.read_text(encoding="utf-8").strip()
    metadata = json.loads(metadata_file.read_text(encoding="utf-8"))

    columns, rows_preview, total_rows = preview_csv(csv_file, limit=10)

    columns_string = ", ".join(columns) if columns else "N/A"

    preview_lines = []
    if rows_preview:
        preview_lines.append(", ".join(columns))
        for row in rows_preview:
            preview_lines.append(", ".join(row))

    data_preview_text = "\n".join(preview_lines) if preview_lines else "No data available."

    # Build prompt
    prompt = PROMPT_TEMPLATE.read_text(encoding="utf-8")
    prompt = prompt.replace("{business_question}", question_text)
    prompt = prompt.replace("{columns_string}", columns_string)
    prompt = prompt.replace("{rows_returned}", str(metadata.get("rows_returned", total_rows)))
    prompt = prompt.replace("{preview_len}", str(len(rows_preview)))
    prompt = prompt.replace("{data_preview}", data_preview_text)
    prompt = prompt.replace("{sql_file_path}", metadata.get("sql_file", "N/A"))

    # Call selected LLM provider
    try:
        result = generate_with_fallback(prompt, provider_name)
    except Exception as exc:
        print("Erreur lors de l'appel au provider LLM :")
        print(exc)
        sys.exit(1)

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save markdown output
    output_md.write_text(result.text.strip(), encoding="utf-8")
    if result.used_fallback:
        print(f"[WARN] {result.fallback_reason}")
        print("[WARN] Falling back to Gemini to preserve the workflow.")

    print(f"[OK] Insights & Actions générés : {output_md}")


def main():
    parser = argparse.ArgumentParser(
        description="Génère un document Insights & Actions à partir d'une question."
    )
    parser.add_argument(
        "--request",
        required=True,
        help="Chemin vers le fichier de requête .txt"
    )
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

    generate_insights_actions(request_file, args.provider)


if __name__ == "__main__":
    main()
