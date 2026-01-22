import os
from typing import Dict, Optional
from tavily import TavilyClient

class WebSearchTool:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if self.api_key:
            self.client = TavilyClient(api_key=self.api_key)
        else:
            self.client = None
    
    def search(self, query: str, max_results: int = 3) -> Dict:
        if not self.client:
            return {
                "success": False,
                "error": "Tavily API key not configured",
                "results": []
            }
        
        try:
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth="basic"
            )
            
            results = []
            for result in response.get("results", []):
                results.append({
                    "title": result.get("title", ""),
                    "content": result.get("content", ""),
                    "url": result.get("url", ""),
                    "score": result.get("score", 0)
                })
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "answer": response.get("answer", "")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Web search failed: {str(e)}",
                "results": []
            }
    
    def get_answer(self, query: str) -> str:
        result = self.search(query, max_results=3)
        
        if result["success"]:
            if result.get("answer"):
                return result["answer"]
            elif result.get("results"):
                content_parts = [r["content"] for r in result["results"][:2]]
                return " ".join(content_parts)
        
        return ""
