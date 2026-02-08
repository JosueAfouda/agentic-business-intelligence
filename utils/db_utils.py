import os
import psycopg2
from dotenv import load_dotenv
#import re

load_dotenv()

def run_query(sql: str):
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    with conn:
        with conn.cursor() as cur:
            cur.execute(sql)
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

