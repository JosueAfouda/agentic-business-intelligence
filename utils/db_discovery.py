from typing import List
from utils.db_utils import run_query

def list_databases() -> List[str]:
    """
    Lists all non-template databases in the PostgreSQL server.

    Returns:
        A list of database names.
    """
    sql = "SELECT datname FROM pg_database WHERE datistemplate = false;"
    try:
        columns, rows = run_query(sql, "postgres")
        return [row[0] for row in rows]
    except Exception as e:
        print(f"Error listing databases: {e}")
        return []

def list_schemas(database_name: str) -> List[str]:
    """
    Lists all schemas in the given database, excluding system schemas.

    Returns:
        A list of schema names.
    """
    sql = """
        SELECT schema_name 
        FROM information_schema.schemata 
        WHERE schema_name NOT IN ('information_schema', 'pg_catalog')
          AND schema_name NOT LIKE 'pg_toast%'
          AND schema_name NOT LIKE 'pg_temp%'
        ORDER BY schema_name;
    """
    try:
        columns, rows = run_query(sql, database_name)
        return [row[0] for row in rows]
    except Exception as e:
        print(f"Error listing schemas for database {database_name}: {e}")
        return []
