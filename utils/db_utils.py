import os
import psycopg2
from dotenv import load_dotenv
#import re

load_dotenv()

def get_connection(database_name: str):
    """Establishes a connection to a specific database."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=database_name,
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def run_query(sql: str, database_name: str, params: tuple = None):
    """Runs a SQL query on a specific database."""
    conn = get_connection(database_name)
    with conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            if cur.description:
                rows = cur.fetchall()
                columns = [desc[0] for desc in cur.description]
            else:
                rows = []
                columns = []
    conn.close()
    return columns, rows




#def clean_sql(sql: str) -> str:
    #sql = re.sub(r"```(?:sql)?", "", sql)  # supprime ```sql
    # transforme /* ... */ en -- ligne par ligne
    #def replace_comment(match):
        #lines = match.group(0)[2:-2].splitlines()
        #return "\n".join(["-- " + line.strip() for line in lines])
    #sql = re.sub(r"/\*.*?\*/", replace_comment, sql, flags=re.DOTALL)
    #return sql

