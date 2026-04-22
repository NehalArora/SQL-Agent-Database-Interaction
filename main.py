code :
import streamlit as st
import sqlite3
import pandas as pd
import os
from openai import OpenAI
from langgraph.graph import StateGraph

# ------------------ API ------------------
API_KEY = os.getenv("SQL_KEY")

if not API_KEY:
    st.error("❌ API key not found. Set SQL_KEY in terminal.")
    st.stop()

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# ------------------ DATABASE ------------------
conn = sqlite3.connect("Chinook_Sqlite.sqlite")

# ------------------ SCHEMA ------------------
def get_schema():
    schema = ""
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchall()

    for t in tables:
        table = t[0]
        cols = conn.execute(f"PRAGMA table_info({table});").fetchall()
        schema += f"\nTable {table}: "
        for col in cols:
            schema += f"{col[1]}, "
    return schema

# ------------------ CLEAN SQL ------------------
def clean_sql(sql):
    sql = sql.replace("```sql", "").replace("```", "")
    sql = sql.replace("SQL", "").strip()

    if "select" in sql.lower():
        sql = sql[sql.lower().find("select"):]

    return sql

# ------------------ STATE ------------------
class AgentState(dict):
    pass

# ------------------ PLANNER ------------------
def planner(state):
    question = state.get("question", "")
    schema = get_schema()

    if not question:
        state["error"] = "No question provided"
        return state

    prompt = f"""
Generate ONLY valid SQLite SQL.

Rules:
- Use ONLY given schema
- Do NOT invent tables
- Return ONLY SQL

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

    raw_sql = response.choices[0].message.content
    state["sql"] = clean_sql(raw_sql)

    return state

# ------------------ VALIDATOR ------------------
def validator(state):
    sql = state.get("sql", "")

    if "select" not in sql.lower():
        state["error"] = "Invalid SQL generated"
    else:
        state["valid"] = True

    return state

# ------------------ EXECUTOR ------------------
def executor(state):
    if "error" in state:
        return state

    try:
        df = pd.read_sql_query(state["sql"], conn)
        state["result"] = df
    except Exception as e:
        state["error"] = str(e)

    return state

# ------------------ EXPLAINER ------------------
def explainer(state):
    if "error" in state:
        return state

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        max_tokens=25,
        messages=[{"role": "user", "content": f"Explain in one line:\n{state['sql']}"}]
    )

    state["explanation"] = response.choices[0].message.content.strip()
    return state

# ------------------ LANGGRAPH FLOW ------------------
builder = StateGraph(dict)

builder.add_node("planner", planner)
builder.add_node("validator", validator)
builder.add_node("executor", executor)
builder.add_node("explainer", explainer)

builder.set_entry_point("planner")

builder.add_edge("planner", "validator")
builder.add_edge("validator", "executor")
builder.add_edge("executor", "explainer")

graph = builder.compile()

# ------------------ UI ------------------
st.title("🧠 Multi-Agent SQL AI (LangGraph + MCP Style)")

question = st.text_input("Ask your question:")

if st.button("Run"):
    if question:
        state = {"question": question}
        output = graph.invoke(state)

        if "error" in output:
            st.error(output["error"])
        else:
            st.subheader("🔹 SQL")
            st.code(output["sql"])

            st.subheader("🔹 Explanation")
            st.write(output["explanation"])

            st.subheader("🔹 Result")
            st.dataframe(output["result"])
