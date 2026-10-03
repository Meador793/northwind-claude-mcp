import os

import psycopg2
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("postgres-mcp-server")


def get_connection():
    """Open a read-only connection to the database."""
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
    )
    conn.set_session(readonly=True, autocommit=True)
    return conn


def run_query(sql: str, params=None) -> list[dict]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            if cur.description is None:
                return []
            columns = [d[0] for d in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]
    finally:
        conn.close()


@mcp.tool()
def execute_sql(query: str) -> list[dict]:
    """Execute a SQL query over a read-only connection and return the rows."""
    return run_query(query)


@mcp.tool()
def list_tables() -> list[str]:
    """List all tables in the public schema."""
    rows = run_query(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'public' AND table_type = 'BASE TABLE' "
        "ORDER BY table_name"
    )
    return [r["table_name"] for r in rows]


@mcp.tool()
def get_schema(table: str) -> list[dict]:
    """Get column names, types, nullability and defaults for a table."""
    return run_query(
        "SELECT column_name, data_type, is_nullable, column_default "
        "FROM information_schema.columns "
        "WHERE table_schema = 'public' AND table_name = %s "
        "ORDER BY ordinal_position",
        (table,),
    )


mcp.run()
