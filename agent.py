import sqlite3
import pandas as pd
from openai import OpenAI
import os

from google.colab import userdata
from openai import OpenAI

client = OpenAI(
    api_key=userdata.get("SQL_KEY"),   # 👈 must match EXACTLY
    base_url="https://api.groq.com/openai/v1"
)

# ------------------ DATABASE ------------------
conn = sqlite3.connect("chinook.db")
cursor = conn.cursor()

# ------------------ GET TABLES ------------------
def get_tables():
    tables = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchall()
    return [t[0] for t in tables]

# ------------------ GET SCHEMA ------------------
def get_schema(tables):
    schema = ""
    for table in tables:
        cols = cursor.execute(f"PRAGMA table_info({table});").fetchall()
        schema += f"\nTable {table}: "
        for col in cols:
            schema += f"{col[1]}, "
    return schema

# ------------------ GENERATE SQL ------------------
def generate_sql(question):
    tables = get_tables()
    schema = get_schema(tables)

    prompt = f"""
You are an expert SQL generator for SQLite.

IMPORTANT RULES:
- Use ONLY the tables provided
- DO NOT invent table names
- ONLY return SQL query
- DO NOT explain anything

Schema:
{schema}

Question:
{question}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )

    sql = response.choices[0].message.content.strip()

    # Clean SQL if model adds formatting
    sql = sql.split("```")[-1] if "```" in sql else sql
    sql = sql.replace("sql", "").strip()

    return sql

# ------------------ FIX SQL ------------------
def fix_sql(query, error):
    prompt = f"""
Fix this SQL query based on error.

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
    fixed = fixed.replace("```", "").strip()

    return fixed

# ------------------ RUN QUERY ------------------
def run_query(sql):
    try:
        df = pd.read_sql_query(sql, conn)
        return df
    except Exception as e:
        return f"Error: {str(e)}"

# ------------------ MAIN AGENT ------------------
def ask_agent(question):
    print("\n==============================")
    print(f"QUESTION: {question}")

    # Step 1: Generate SQL
    sql = generate_sql(question)
    print("\n🔹 Generated SQL:")
    print(sql)

    # Step 2: Run query
    result = run_query(sql)

    # Step 3: Auto-fix if error
    if isinstance(result, str) and "Error" in result:
        print("\n⚠️ Fixing query...")

        fixed_sql = fix_sql(sql, result)
        print("\n🔹 Fixed SQL:")
        print(fixed_sql)

        result = run_query(fixed_sql)

    # Step 4: Display result
    print("\n🔹 Result:\n")

    if isinstance(result, str):
        print("❌ Still Error:", result)
        print("\n💡 Try rephrasing your question")
    else:
        print(result.head(10))   # clean output

# ------------------ TEST ------------------

ask_agent("Top selling tracks")
