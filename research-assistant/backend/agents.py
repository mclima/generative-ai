from llm import llm
from tools import search_tool, scrape_webpages
from fallback import generate_fallback_response
import time

def search_agent(state):
    topic = state.get("topic", "")
    
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            result = search_tool.invoke({"query": topic})
            
            if result and len(result) > 0:
                return {"topic": topic, "search_results": result, "documents": [], "search_error": None}
            else:
                if attempt < max_retries:
                    time.sleep(1)
                    continue
                    
        except Exception as e:
            if attempt < max_retries:
                time.sleep(2)
                continue
            return {"topic": topic, "search_results": [], "documents": [], "search_error": str(e)}
    
    return {"topic": topic, "search_results": [], "documents": [], "search_error": "No results after retries"}

def scraper_agent(state):
    search_results = state.get("search_results", [])
    search_error = state.get("search_error")
    topic = state.get("topic", "")
    
    if search_error:
        return {"topic": topic, "documents": [], "scraper_error": "Skipped due to search failure"}
    
    if not search_results:
        return {"topic": topic, "documents": [], "scraper_error": "No search results available"}
    
    urls = [r.get("url") for r in search_results if "url" in r][:3]
    
    if not urls:
        return {"topic": topic, "documents": [], "scraper_error": "No valid URLs"}
    
    try:
        documents = scrape_webpages(urls)
        
        if documents and len(documents) > 0:
            return {"topic": topic, "documents": documents, "scraper_error": None}
        else:
            return {"topic": topic, "documents": [], "scraper_error": "No content extracted"}
            
    except Exception as e:
        return {"topic": topic, "documents": [], "scraper_error": str(e)}

def writer_agent(state):
    notes = state.get("notes", "")
    topic = state.get("topic", "")
    scraper_error = state.get("scraper_error")
    search_error = state.get("search_error")
    
    if not notes or notes.strip() == "":
        errors = {
            "search_error": search_error or "No content available",
            "scraper_error": scraper_error
        }
        fallback_content = generate_fallback_response(topic, errors)
        return {"topic": topic, "draft": fallback_content, "writer_error": None, "is_fallback": True}
    else:
        prompt = f"""Write a detailed outline for '{topic}' based on these notes. 

Format requirements:
- Start with ## {topic} as the title
- Use ### for section headings
- Under each section, provide a 1-2 sentence summary explaining the key details
- Base everything strictly on the provided notes - no new facts
- Keep summaries concise and informative

Notes:
{notes}"""
    
    max_retries = 2
    for attempt in range(1, max_retries + 1):
        try:
            response = llm.invoke(prompt)
            
            if response and response.content:
                return {"topic": topic, "draft": response.content, "writer_error": None}
            else:
                if attempt < max_retries:
                    time.sleep(1)
                    continue
                    
        except Exception as e:
            if attempt < max_retries:
                time.sleep(2)
                continue
            errors = {
                "search_error": search_error,
                "scraper_error": scraper_error,
                "writer_error": str(e)
            }
            fallback_content = generate_fallback_response(topic, errors)
            return {"topic": topic, "draft": fallback_content, "writer_error": str(e), "is_fallback": True}
    
    errors = {
        "search_error": search_error,
        "scraper_error": scraper_error,
        "writer_error": "Max retries exceeded"
    }
    fallback_content = generate_fallback_response(topic, errors)
    return {"topic": topic, "draft": fallback_content, "writer_error": "Max retries exceeded", "is_fallback": True}

def editor_agent(state):
    draft = state.get("draft", "")
    writer_error = state.get("writer_error")
    is_fallback = state.get("is_fallback", False)
    
    if is_fallback:
        return {"final_output": draft, "editor_error": None}
    
    if writer_error:
        return {"final_output": draft, "editor_error": "Skipped due to writer error"}
    
    if not draft or draft.strip() == "":
        return {"final_output": "Error: No content to edit", "editor_error": "No draft available"}
    
    max_retries = 2
    for attempt in range(1, max_retries + 1):
        try:
            prompt = f"Edit for clarity. Remove fluff. Preserve facts:\n\n{draft}"
            response = llm.invoke(prompt)
            
            if response and response.content:
                return {"final_output": response.content, "editor_error": None}
            else:
                if attempt < max_retries:
                    time.sleep(1)
                    continue
                    
        except Exception as e:
            if attempt < max_retries:
                time.sleep(2)
                continue
            return {"final_output": draft, "editor_error": str(e)}
    
    return {"final_output": draft, "editor_error": "Max retries exceeded"}
