from crewai import Agent
from langchain.tools import BaseTool, tool
from pydantic import BaseModel

print(f"Agent fields: {Agent.model_fields.keys()}")
print(f"Agent tool field: {Agent.model_fields['tools']}")

@tool
def dummy():
    """test"""
    return "ok"

print(f"Dummy tool type: {type(dummy)}")
print(f"Is dummy BaseTool? {isinstance(dummy, BaseTool)}")

# Check where BaseTool comes from
import langchain_core.tools
print(f"LangChain Core BaseTool: {langchain_core.tools.BaseTool}")

import langchain.tools
print(f"LangChain BaseTool: {langchain.tools.BaseTool}")

# Check if CrewAI uses a specific BaseTool
try:
    from crewai.agents.agent_builder.base_agent import BaseAgent
    # (Just guessing paths)
except:
    pass
