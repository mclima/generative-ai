from pydantic import BaseModel

class ResearchRequest(BaseModel):
    topic: str

class ResearchResponse(BaseModel):
    outline: str
