import subprocess
from pathlib import Path

REQUESTS_DIR = Path("requests")
SQL_DIR = Path("sql")
SCHEMA_FILE = Path("schema/dvdrental_schema.md")

PROMPT_TEMPLATE = Path("scripts/prompt_template.txt")

def generate_sql(question_file: Path):
    sql_file = SQL_DIR / (question_file.stem + ".sql")
    
    if sql_file.exists():
        print(f"[SKIP] {sql_file} existe déjà, pas de génération")
        return

    # Lecture du prompt template
    prompt = PROMPT_TEMPLATE.read_text()
    prompt = prompt.replace("{{SCHEMA}}", SCHEMA_FILE.read_text())
    prompt = prompt.replace("{{QUESTION}}", question_file.read_text())
    prompt = prompt.replace("{{SQL_PATH}}", str(sql_file))

    # Appel à Gemini CLI pour générer le SQL
    result = subprocess.run(
        ["gemini", "run"],
        input=prompt,
        text=True,
        capture_output=True
    )

    sql_file.parent.mkdir(exist_ok=True)
    sql_file.write_text(result.stdout)
    print(f"[OK] SQL généré pour {question_file.name}")

def main():
    for q in REQUESTS_DIR.glob("*.txt"):
        generate_sql(q)

if __name__ == "__main__":
    main()
