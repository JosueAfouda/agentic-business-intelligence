from typing import List
from utils.db_utils import run_query

def list_schemas(database_name: str) -> List[str]:
    """
    Lists all non-system schemas in a specific database.

    Args:
        database_name: The name of the database to inspect.

    Returns:
        A list of schema names.
    """
    sql = """
        SELECT schema_name
        FROM information_schema.schemata
        WHERE schema_name NOT IN ('pg_catalog', 'information_schema');
    """
    try:
        columns, rows = run_query(sql, database_name)
        return [row[0] for row in rows]
    except Exception as e:
        print(f"Error listing schemas for database '{database_name}': {e}")
        return []
