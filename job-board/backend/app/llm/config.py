import os
from langchain_openai import ChatOpenAI

class LLMConfig:
    def __init__(self):
        self.model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.3"))
    
    def get_llm(self):
        return ChatOpenAI(
            model=self.model,
            temperature=self.temperature,
            api_key=os.getenv("OPENAI_API_KEY")
        )

llm_config = LLMConfig()
