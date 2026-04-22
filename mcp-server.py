import sqlite3
import pandas as pd
from openai import OpenAI
from google.colab import userdata

# ------------------ API ------------------
client = OpenAI(
    api_key=userdata.get("SQL_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# ------------------ DATABASE ------------------
conn = sqlite3.connect("Chinook.db")   # <-- your uploaded file name

# ------------------ SQL TOOL ------------------
def sql_tool(query):
    try:
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        return f"Error: {str(e)}"

# ------------------ AUTO TABLE DETECTION ------------------
def get_tables():
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchall()
    return [t[0] for t in tables]

# ------------------ AUTO SCHEMA ------------------
def get_schema():
    schema = ""
    tables = get_tables()

    for table in tables:
        cols = conn.execute(f"PRAGMA table_info({table});").fetchall()
        schema += f"\nTable {table}: "
        for col in cols:
            schema += f"{col[1]}, "

    return schema

# ------------------ CLEAN SQL ------------------
def clean_sql(sql):
    sql = sql.replace("```", "")
    sql = sql.replace("sql", "")
    return sql.strip()

# ------------------ MCP GENERATE ------------------
def generate_mcp_response(question):
    schema = get_schema()
    tables = get_tables()

    prompt = f"""
You are a STRICT SQLite SQL generator.

IMPORTANT:
- Use ONLY these tables:
{tables}

- Use EXACT names (case sensitive)
- DO NOT change table names
- DO NOT invent tables
- DO NOT add 'sql'
- DO NOT explain anything

Schema:
{schema}

Question:
{question}

Return format:
TOOL: SQL_TOOL
QUERY: SELECT ...
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()

# ------------------ PARSE ------------------
def parse_mcp_output(response):
    lines = response.split("\n")
    query = ""

    for line in lines:
        if "QUERY:" in line:
            query = line.replace("QUERY:", "").strip()

    return clean_sql(query)

# ------------------ FIX SQL ------------------
def fix_sql(query, error):
    schema = get_schema()
    tables = get_tables()

    prompt = f"""
Fix this SQL query.

IMPORTANT:
- Use ONLY these tables:
{tables}
- Use EXACT names
- DO NOT add 'sql'

Schema:
{schema}

Query:
{query}

Error:
{error}

Return ONLY corrected SQL.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )

    fixed = response.choices[0].message.content.strip()
    return clean_sql(fixed)

# ------------------ MCP AGENT ------------------
def mcp_agent(question):
    print("\n==============================")
    print(f"QUESTION: {question}")

    # Step 1: Generate MCP response
    response = generate_mcp_response(question)

    print("\n🔹 MCP Response:")
    print(response)

    # Step 2: Extract SQL
    sql = parse_mcp_output(response)

    print("\n🔹 SQL:")
    print(sql)

    # Step 3: Execute
    result = sql_tool(sql)

    # Step 4: Auto-fix if error
    if isinstance(result, str) and "Error" in result:
        print("\n⚠️ Fixing query...")

        fixed_sql = fix_sql(sql, result)

        print("\n🔹 Fixed SQL:")
        print(fixed_sql)

        result = sql_tool(fixed_sql)

    # Step 5: Output
    print("\n🔹 Result:\n")

    if isinstance(result, str):
        print("❌ Still Error:", result)
    else:
        print(result.head(10))

# ------------------ TEST ------------------

mcp_agent("Top selling tracks")
