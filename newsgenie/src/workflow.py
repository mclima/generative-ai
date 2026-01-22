from typing import TypedDict, List, Optional, Annotated
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import operator
from src.news_api import GNewsAPI
from src.web_search import WebSearchTool

class AgentState(TypedDict):
    messages: Annotated[List[str], operator.add]
    user_query: str
    query_type: str
    news_category: Optional[str]
    news_results: Optional[dict]
    web_results: Optional[dict]
    final_response: str
    error: Optional[str]

class NewsGenieWorkflow:
    def __init__(self, openai_api_key: str, gnews_api_key: str, tavily_api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=openai_api_key,
            temperature=0.7
        )
        self.news_api = GNewsAPI(api_key=gnews_api_key)
        self.web_search = WebSearchTool(api_key=tavily_api_key)
        self.graph = self._build_graph()
    
    def _classify_query(self, state: AgentState) -> AgentState:
        user_query = state["user_query"]
        
        system_prompt = """You are a query classifier. Analyze the user's query and determine:
1. Query Type: Choose ONE of these:
   - NEWS: User wants recent news articles or headlines (keywords: news, latest, headlines, updates, what's happening)
   - GENERAL: User wants general information, facts, or conversation
   - HYBRID: User wants both news AND general information

2. News Category (if applicable): technology, finance, sports, general, health, science, entertainment

Respond in this exact format:
TYPE: [NEWS/GENERAL/HYBRID]
CATEGORY: [category or NONE]

Examples:
- "What's the latest in technology?" -> TYPE: NEWS, CATEGORY: technology
- "Tell me about artificial intelligence" -> TYPE: GENERAL, CATEGORY: NONE
- "What's happening with Tesla stock and give me background on the company" -> TYPE: HYBRID, CATEGORY: finance"""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_query)
            ]
            
            response = self.llm.invoke(messages)
            content = response.content.strip()
            
            query_type = "GENERAL"
            category = None
            
            for line in content.split("\n"):
                if line.startswith("TYPE:"):
                    query_type = line.split("TYPE:")[1].strip()
                elif line.startswith("CATEGORY:"):
                    cat = line.split("CATEGORY:")[1].strip()
                    if cat != "NONE":
                        category = cat.lower()
            
            state["query_type"] = query_type
            state["news_category"] = category
            
        except Exception as e:
            state["error"] = f"Classification error: {str(e)}"
            state["query_type"] = "GENERAL"
        
        return state
    
    def _fetch_news(self, state: AgentState) -> AgentState:
        category = state.get("news_category", "general")
        
        try:
            news_results = self.news_api.fetch_top_headlines(category=category, max_results=5)
            state["news_results"] = news_results
            
            if not news_results.get("success"):
                state["error"] = news_results.get("error", "Failed to fetch news")
        
        except Exception as e:
            state["error"] = f"News fetch error: {str(e)}"
            state["news_results"] = {"success": False, "articles": []}
        
        return state
    
    def _web_search(self, state: AgentState) -> AgentState:
        user_query = state["user_query"]
        
        try:
            search_results = self.web_search.search(query=user_query, max_results=3)
            state["web_results"] = search_results
            
            if not search_results.get("success"):
                state["error"] = search_results.get("error", "Web search failed")
        
        except Exception as e:
            state["error"] = f"Web search error: {str(e)}"
            state["web_results"] = {"success": False, "results": []}
        
        return state
    
    def _generate_response(self, state: AgentState) -> AgentState:
        user_query = state["user_query"]
        query_type = state["query_type"]
        news_results = state.get("news_results", {})
        web_results = state.get("web_results", {})
        
        context_parts = []
        
        if news_results and news_results.get("success"):
            articles = news_results.get("articles", [])
            if articles:
                context_parts.append("=== NEWS ARTICLES ===")
                for i, article in enumerate(articles[:5], 1):
                    context_parts.append(f"{i}. {article['title']}")
                    context_parts.append(f"   Source: {article['source']}")
                    context_parts.append(f"   {article['description']}")
                    context_parts.append(f"   URL: {article['url']}\n")
        
        if web_results and web_results.get("success"):
            results = web_results.get("results", [])
            if results:
                context_parts.append("=== WEB SEARCH RESULTS ===")
                for i, result in enumerate(results[:3], 1):
                    context_parts.append(f"{i}. {result['title']}")
                    context_parts.append(f"   {result['content'][:200]}...")
                    context_parts.append(f"   URL: {result['url']}\n")
        
        context = "\n".join(context_parts) if context_parts else "No additional context available."
        
        system_prompt = f"""You are NewsGenie, an AI-powered news and information assistant.

User Query: {user_query}
Query Type: {query_type}

Context:
{context}

Instructions:
- Provide a helpful, accurate, and well-structured response
- If news articles are provided, summarize key points and cite sources
- Be conversational but informative
- If no relevant information is found, acknowledge it and provide general guidance
- Format your response with clear sections if appropriate"""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_query)
            ]
            
            response = self.llm.invoke(messages)
            state["final_response"] = response.content
            
        except Exception as e:
            state["error"] = f"Response generation error: {str(e)}"
            state["final_response"] = "I apologize, but I encountered an error generating a response. Please try again."
        
        return state
    
    def _route_query(self, state: AgentState) -> str:
        query_type = state.get("query_type", "GENERAL")
        
        if state.get("error"):
            return "generate_response"
        
        if query_type == "NEWS":
            return "fetch_news"
        elif query_type == "GENERAL":
            return "web_search"
        elif query_type == "HYBRID":
            return "fetch_news"
        else:
            return "web_search"
    
    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(AgentState)
        
        workflow.add_node("classify_query", self._classify_query)
        workflow.add_node("fetch_news", self._fetch_news)
        workflow.add_node("web_search", self._web_search)
        workflow.add_node("generate_response", self._generate_response)
        
        workflow.set_entry_point("classify_query")
        
        workflow.add_conditional_edges(
            "classify_query",
            self._route_query,
            {
                "fetch_news": "fetch_news",
                "web_search": "web_search",
                "generate_response": "generate_response"
            }
        )
        
        workflow.add_edge("fetch_news", "generate_response")
        workflow.add_edge("web_search", "generate_response")
        workflow.add_edge("generate_response", END)
        
        return workflow.compile()
    
    def process_query(self, user_query: str) -> dict:
        initial_state = {
            "messages": [],
            "user_query": user_query,
            "query_type": "",
            "news_category": None,
            "news_results": None,
            "web_results": None,
            "final_response": "",
            "error": None
        }
        
        try:
            result = self.graph.invoke(initial_state)
            return {
                "success": True,
                "response": result.get("final_response", ""),
                "query_type": result.get("query_type", ""),
                "news_results": result.get("news_results"),
                "web_results": result.get("web_results"),
                "error": result.get("error")
            }
        except Exception as e:
            return {
                "success": False,
                "response": f"An error occurred: {str(e)}",
                "error": str(e)
            }
