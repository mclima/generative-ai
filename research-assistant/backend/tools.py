import requests
from bs4 import BeautifulSoup
from langchain_community.tools.tavily_search import TavilySearchResults

search_tool = TavilySearchResults(max_results=5)

def scrape_webpages(urls: list[str]) -> list[str]:
    texts = []
    for url in urls:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        content = " ".join(p.get_text() for p in soup.find_all("p"))
        texts.append(content[:6000])
    return texts
