import os
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from models.stock_models import NewsArticle

class VectorStoreService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
        
        persist_directory = os.path.join(os.path.dirname(__file__), "..", "chroma_db")
        os.makedirs(persist_directory, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        try:
            self.collection = self.client.get_collection("stock_news")
        except:
            self.collection = self.client.create_collection(
                name="stock_news",
                metadata={"description": "Stock news articles for RAG"}
            )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
    
    async def add_news_article(self, symbol: str, article: NewsArticle):
        try:
            text = f"{article.title}\n\n{article.description}"
            
            embedding = self.embeddings.embed_query(text)
            
            self.collection.add(
                embeddings=[embedding],
                documents=[text],
                metadatas=[{
                    "symbol": symbol,
                    "title": article.title,
                    "url": article.url,
                    "published_at": article.published_at,
                    "source": article.source
                }],
                ids=[f"{symbol}_{article.published_at}_{hash(article.title)}"]
            )
        except Exception as e:
            print(f"Error adding article to vector store: {str(e)}")
    
    async def get_relevant_context(self, symbol: str, query: str = "", limit: int = 5) -> str:
        try:
            if not query:
                query = f"Recent news and analysis for {symbol}"
            
            query_embedding = self.embeddings.embed_query(query)
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where={"symbol": symbol}
            )
            
            if not results["documents"] or not results["documents"][0]:
                return ""
            
            context_parts = []
            for doc, metadata in zip(results["documents"][0], results["metadatas"][0]):
                context_parts.append(f"[{metadata.get('source', 'Unknown')}] {doc}")
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            print(f"Error retrieving context: {str(e)}")
            return ""
