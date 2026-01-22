import requests
import os
from typing import List, Dict, Optional
from datetime import datetime

class GNewsAPI:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GNEWS_API_KEY")
        self.base_url = "https://gnews.io/api/v4"
        
    def fetch_top_headlines(self, category: str, max_results: int = 5) -> Dict:
        if not self.api_key:
            return {
                "success": False,
                "error": "GNews API key not configured",
                "articles": []
            }
        
        category_map = {
            "technology": "technology",
            "finance": "business",
            "sports": "sports",
            "general": "general",
            "health": "health",
            "science": "science",
            "entertainment": "entertainment"
        }
        
        mapped_category = category_map.get(category.lower(), "general")
        
        try:
            url = f"{self.base_url}/top-headlines"
            params = {
                "category": mapped_category,
                "lang": "en",
                "max": max_results,
                "apikey": self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            articles = []
            for article in data.get("articles", []):
                articles.append({
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "url": article.get("url", ""),
                    "publishedAt": article.get("publishedAt", ""),
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "image": article.get("image", "")
                })
            
            return {
                "success": True,
                "category": category,
                "articles": articles,
                "total_results": len(articles)
            }
            
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request timeout - GNews API is taking too long to respond",
                "articles": []
            }
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                return {
                    "success": False,
                    "error": "Rate limit exceeded - Please try again later",
                    "articles": []
                }
            return {
                "success": False,
                "error": f"HTTP error: {str(e)}",
                "articles": []
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to fetch news: {str(e)}",
                "articles": []
            }
    
    def search_news(self, query: str, max_results: int = 5) -> Dict:
        if not self.api_key:
            return {
                "success": False,
                "error": "GNews API key not configured",
                "articles": []
            }
        
        try:
            url = f"{self.base_url}/search"
            params = {
                "q": query,
                "lang": "en",
                "max": max_results,
                "apikey": self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            articles = []
            for article in data.get("articles", []):
                articles.append({
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "url": article.get("url", ""),
                    "publishedAt": article.get("publishedAt", ""),
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "image": article.get("image", "")
                })
            
            return {
                "success": True,
                "query": query,
                "articles": articles,
                "total_results": len(articles)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to search news: {str(e)}",
                "articles": []
            }
