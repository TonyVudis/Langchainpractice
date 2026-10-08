import pandas as pd
import os
from dotenv import load_dotenv
from typing import TypedDict, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, START, END

load_dotenv()
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
llm = ChatGoogleGenerativeAI(model=MODEL, temperature=0)
from langchain_google_genai import ChatGoogleGenerativeAI


class SQLQuery(BaseModel):
    sql: str = Field(description = "One read-only SQLite SELECT statement")

sql_prompt = ChatPromptTemplate.from_messages([
    ("system", "Your write SQlite queires. Use only this schema: \n{schema}\n"
                "Business definitions:\n{definitions}\n"
               "Return one SELECT statement. Never modify data."),
    ("human", "{question}\n\n{feedback}")
])

sql_chain = sql_prompt | llm.with_structured_output(SQLQuery)

def write_sql(question, prev_sql, error):
    feedback = ""
    if error:
        feedback = (f"Your previous query failed.\nQuery: {prev_sql}\n"
                    f"Error: {error}\nWrite a corrected query.")
    return sql_chain.invoke({"schema": schema, "definitions": DEFINITIONS,
                             "question": question, "feedback": feedback}).sql

summary_chain = (
    ChatPromptTemplate.from_template(
        "Question: {question}\nSQL:\n{sql}\nResult:\n{table}\n\n"
        "Summarize in 2 sentences. Use only numbers in the table.")
    | llm | StrOutputParser()
)
def write_summary(question, sql, table):
    return summary_chain.invoke({"question": question, "sql": sql, "table": table})

MAX_ATTEMPTS = 3

class State(TypedDict):
    question: str
    sql: str
    error: Optional[str]
    table: str
    attempts: int
    answer: str

def generate_sql(state: State):
    sql = write_sql(state["question"], state.get("sql"), state.get("error"))
    return {"sql": sql, "attempts": state.get("attempts", 0) + 1, "error": None}

def run_sql(state: State):
    if not is_safe(state["sql"]):
        return {"error": "Rejected: not a single read-only SELECT"}
    try:
        df = pd.read_sql(state["sql"], conn)
        return {"table": df.head(30).to_string(index=False), "error": None}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}

def narrate(state: State):
    return {"answer": write_summary(state["question"], state["sql"], state["table"])}

def give_up(state: State):
    return {"answer": f"Could not produce a valid query after {state['attempts']} "
                      f"attempts. Last error: {state['error']}"}

def route_after_run(state: State):
    if state["error"] is None:
        return "narrate"
    return "generate_sql" if state["attempts"] < MAX_ATTEMPTS else "give_up"

g = StateGraph(State)
g.add_node("generate_sql", generate_sql)
g.add_node("run_sql", run_sql)
g.add_node("narrate", narrate)
g.add_node("give_up", give_up)

g.add_edge(START, "generate_sql")
g.add_edge("generate_sql", "run_sql")
g.add_conditional_edges("run_sql", route_after_run,
                        {"narrate": "narrate",
                         "generate_sql": "generate_sql",
                         "give_up": "give_up"})
g.add_edge("narrate", END)
g.add_edge("give_up", END)

app = g.compile()