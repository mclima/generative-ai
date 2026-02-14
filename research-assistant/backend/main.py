from fastapi import FastAPI
from schemas import ResearchRequest, ResearchResponse
from graph import app as graph_app
from fallback import is_valid_topic

app = FastAPI()

@app.post("/research", response_model=ResearchResponse)
async def research(req: ResearchRequest):
    # Validate topic before processing
    if not is_valid_topic(req.topic):
        return {"outline": """## Invalid Research Topic

**Please provide a valid research topic.** Your query appears to contain random characters or is not a meaningful research question.

**Examples of valid topics:**
- "climate change effects on polar bears"
- "latest developments in quantum computing"  
- "history of the Roman Empire"
- "benefits of Mediterranean diet"

Please try again with a clear, specific topic."""}
    
    try:
        result = await graph_app.ainvoke({"topic": req.topic})
        return {"outline": result["final_output"]}
        
    except Exception as e:
        raise
