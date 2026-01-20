from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from routes import stock_routes
from services.vector_store import VectorStoreService

load_dotenv()

app = FastAPI(
    title="Stock Agent API",
    description="AI-powered US stock analysis API with RAG capabilities",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stock_routes.router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    vector_service = VectorStoreService()
    app.state.vector_service = vector_service

@app.get("/")
async def root():
    return {
        "message": "Stock Agent API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
