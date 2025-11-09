from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage
from ..core.config import settings
from .prompts import SYSTEM_PROMPT, USER_HINTS
from .tools import TOOLS
import os

# Choose LLM
try:
    from langchain_openai import ChatOpenAI
    _openai_ok = settings.OPENAI_API_KEY is not None
except Exception:
    _openai_ok = False

if _openai_ok:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
else:
    from langchain_ollama import ChatOllama
    llm = ChatOllama(model="llama3.1:8b-instruct", temperature=0.2)

llm_with_tools = llm.bind_tools(TOOLS)

def call_model(state: MessagesState):
    msgs = [SystemMessage(content=f"{SYSTEM_PROMPT}\n\n{USER_HINTS}")] + state["messages"]
    ai = llm_with_tools.invoke(msgs)
    return {"messages": [ai]}

run_tools = ToolNode(TOOLS)

def should_continue(state: MessagesState) -> Literal["tools", "end"]:
    if not state["messages"]:
        return "end"
    last = state["messages"][-1]
    if getattr(last, "tool_calls", None):
        return "tools"
    return "end"

def build_graph():
    g = StateGraph(MessagesState)
    g.add_node("model", call_model)
    g.add_node("tools", run_tools)
    g.set_entry_point("model")
    g.add_conditional_edges("model", should_continue, {"tools": "tools", "end": END})
    g.add_edge("tools", "model")
    return g.compile()

app_graph = build_graph()
