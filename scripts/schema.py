import argparse
from pathlib import Path
import sys

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils.db_utils import run_query

def generate_schema(database_name: str, schema_name: str = "public"):
    schema_path = Path(f"schema/{database_name}__{schema_name}_schema.md")

    queries = {
        "tables": ("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s
              AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """, (schema_name,)),

        "columns": ("""
            SELECT
                c.table_name,
                c.column_name,
                c.data_type,
                c.is_nullable
            FROM information_schema.columns c
            JOIN information_schema.tables t
              ON c.table_name = t.table_name
             AND c.table_schema = t.table_schema
            WHERE c.table_schema = %s
              AND t.table_type = 'BASE TABLE'
            ORDER BY c.table_name, c.ordinal_position;
        """, (schema_name,)),

        "constraints": ("""
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
            WHERE tc.table_schema = %s
              AND t.table_type = 'BASE TABLE'
            ORDER BY tc.table_name, tc.constraint_type;
        """, (schema_name,))
    }

    content = [f"# Schéma de la base {database_name} (Schema: {schema_name})\n"]
    content.append(
        "_Note : seules les tables physiques (BASE TABLE) sont prises en compte. "
        "Les vues SQL sont volontairement exclues._\n"
    )

    for section, (sql, params) in queries.items():
        _, rows = run_query(sql, database_name, params)
        content.append(f"\n## {section.upper()}\n")
        for row in rows:
            # Fully qualify table names in the output
            row_list = list(row)
            if section in ["tables", "columns", "constraints"]:
                row_list[0] = f"{schema_name}.{row_list[0]}"
            if section == "constraints" and row_list[3] and row_list[3] != 'None':
                 row_list[3] = f"{schema_name}.{row_list[3]}"

            content.append("- " + " | ".join(map(str, row_list)))

    schema_path.parent.mkdir(exist_ok=True)
    schema_path.write_text("\n".join(content))
    print(f"Schema for database '{database_name}' (schema '{schema_name}') generated at {schema_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate schema for a given database.")
    parser.add_argument("--database", required=True, help="The name of the database.")
    parser.add_argument("--schema", default="public", help="The name of the schema (default: public).")
    args = parser.parse_args()
    generate_schema(args.database, args.schema)
