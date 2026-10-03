# northwind-claude-mcp

Connects Claude to three things through the Model Context Protocol (MCP): a
PostgreSQL database (the Northwind sample data), GitHub, and the local
filesystem. With all three available in one session, Claude can answer a
question about the data, look at the code or files around it, and work with the
repo without me copying anything between tools.

## Setup

1. **Start Postgres in Docker**

   ```
   docker run --name northwind -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres
   docker exec -it northwind createdb -U postgres northwind
   ```

2. **Load the Northwind data.** Download `northwind.sql` from
   [github.com/pthom/northwind_psql](https://github.com/pthom/northwind_psql)
   and load it:

   ```
   docker exec -i northwind psql -U postgres -d northwind < northwind.sql
   ```

   The file is in `.gitignore`, so it isn't stored in this repo.

3. **Create a `.env`** in the project root (also git-ignored):

   ```
   DB_NAME=northwind
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_HOST=localhost
   DB_PORT=5432
   ```

4. **Install the requirements** in a virtual environment:

   ```
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

5. **Create a GitHub token.** In GitHub, go to Settings > Developer settings >
   Personal access tokens and make one with access to the repos you want Claude
   to use. Then set it as an environment variable named `GITHUB_PAT`.

6. **Configure MCP.** Copy `.mcp.json` into your project and change the absolute
   paths (the Python interpreter, `main.py`, and the filesystem folder) to match
   where you cloned this. Restart Claude Code so it picks up the servers.

## Tools in `postgres-mcp-server/main.py`

- `execute_sql(query)`: runs any SQL query and returns the rows.
- `list_tables()`: lists the tables in the `public` schema.
- `get_schema(table)`: returns the columns, types, nullability and defaults
  for one table.
- `top_customers(n)`: my own addition. Ranks customers by total revenue after
  discounts, so a common question doesn't need hand-written SQL each time.

## Read-only

Every connection is opened with `readonly=True`, so Claude can query the
database but any `INSERT`, `UPDATE`, `DELETE` or DDL statement is rejected by
Postgres.

## Credit

Built following the MCP + Postgres workshop pattern.
