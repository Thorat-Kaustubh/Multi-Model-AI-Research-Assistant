from crewai import Agent
import inspect

tool_type = Agent.model_fields['tools'].annotation
# tool_type is list[BaseTool]
base_tool_type = tool_type.__args__[0]
print(f"BaseTool type: {base_tool_type}")
print(f"Module: {inspect.getmodule(base_tool_type)}")
print(f"File: {inspect.getfile(base_tool_type)}")

from langchain_core.tools import BaseTool as LCBTool
print(f"Is same? {base_tool_type is LCBTool}")
