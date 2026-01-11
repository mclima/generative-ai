from fastapi import FastAPI
from schemas import ResearchRequest, ResearchResponse
from graph import app as graph_app

app = FastAPI()

@app.post("/research", response_model=ResearchResponse)
async def research(req: ResearchRequest):
    print("➡️ Starting LangGraph execution")
    result = await graph_app.ainvoke({"topic": req.topic})
    print("✅ LangGraph completed")
    return {"outline": result["final_output"]}
