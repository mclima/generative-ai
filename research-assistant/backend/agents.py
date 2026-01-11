from llm import llm
from tools import search_tool, scrape_webpages

def search_agent(state):
    topic = state.get("topic", "")
    result = search_tool.invoke({"query": topic})
    return {"search_results": result, "documents": []}

def scraper_agent(state):
    search_results = state.get("search_results", [])
    urls = [r.get("url") for r in search_results if "url" in r][:3]
    if urls:
        documents = scrape_webpages(urls)
        return {"documents": documents}
    return {"documents": []}

def writer_agent(state):
    notes = state.get("notes", "")
    topic = state.get("topic", "")
    prompt = f"""Write a detailed outline for '{topic}' based on these notes. 

Format requirements:
- Use bullet points for main topics
- Under each bullet point, provide a 1-2 sentence summary explaining the key details
- Base everything strictly on the provided notes - no new facts
- Keep summaries concise and informative

Notes:
{notes}"""
    response = llm.invoke(prompt)
    return {"draft": response.content}

def editor_agent(state):
    draft = state.get("draft", "")
    prompt = f"Edit for clarity. Remove fluff. Preserve facts:\n\n{draft}"
    response = llm.invoke(prompt)
    return {"final_output": response.content}
