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
