import argparse
from utils.db_utils import run_query
from pathlib import Path

def generate_schema(database_name: str):
    schema_path = Path(f"schema/{database_name}_schema.md")

    queries = {
        "tables": """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """,

        "columns": """
            SELECT
                c.table_name,
                c.column_name,
                c.data_type,
                c.is_nullable
            FROM information_schema.columns c
            JOIN information_schema.tables t
              ON c.table_name = t.table_name
             AND c.table_schema = t.table_schema
            WHERE c.table_schema = 'public'
              AND t.table_type = 'BASE TABLE'
            ORDER BY c.table_name, c.ordinal_position;
        """,

        "constraints": """
            SELECT
                tc.table_name,
                tc.constraint_type,
                kcu.column_name,
                ccu.table_name AS foreign_table,
                ccu.column_name AS foreign_column
            FROM information_schema.table_constraints tc
            JOIN information_schema.tables t
              ON tc.table_name = t.table_name
             AND tc.table_schema = t.table_schema
            LEFT JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
            LEFT JOIN information_schema.constraint_column_usage ccu
              ON ccu.constraint_name = tc.constraint_name
             AND ccu.table_schema = tc.table_schema
            WHERE tc.table_schema = 'public'
              AND t.table_type = 'BASE TABLE'
            ORDER BY tc.table_name, tc.constraint_type;
        """
    }

    content = [f"# Schéma de la base {database_name}\n"]
    content.append(
        "_Note : seules les tables physiques (BASE TABLE) sont prises en compte. "
        "Les vues SQL sont volontairement exclues._\n"
    )

    for section, sql in queries.items():
        _, rows = run_query(sql, database_name)
        content.append(f"\n## {section.upper()}\n")
        for row in rows:
            content.append("- " + " | ".join(map(str, row)))

    schema_path.parent.mkdir(exist_ok=True)
    schema_path.write_text("\n".join(content))
    print(f"Schema for database '{database_name}' generated at {schema_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate schema for a given database.")
    parser.add_argument("--database", required=True, help="The name of the database.")
    args = parser.parse_args()
    generate_schema(args.database)
