from langgraph.graph import StateGraph
from agents import (
    search_agent,
    scraper_agent,
    writer_agent,
    editor_agent
)

def note_taker(state):
    documents = state.get("documents", [])
    scraper_error = state.get("scraper_error")
    topic = state.get("topic", "")
    
    if scraper_error or not documents:
        return {"topic": topic, "notes": ""}
    
    notes = "\n".join(documents)
    return {"topic": topic, "notes": notes}

graph = StateGraph(dict)

graph.add_node("search", search_agent)
graph.add_node("scrape", scraper_agent)
graph.add_node("notes", note_taker)
graph.add_node("write", writer_agent)
graph.add_node("edit", editor_agent)

graph.set_entry_point("search")
graph.add_edge("search", "scrape")
graph.add_edge("scrape", "notes")
graph.add_edge("notes", "write")
graph.add_edge("write", "edit")

app = graph.compile()
