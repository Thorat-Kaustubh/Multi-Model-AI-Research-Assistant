from crewai.tools import BaseTool
from pydantic import Field
from shared.configuration import BaseConfiguration
from shared.compression import compress_text

# --- Custom Tools ---

class ChromaSearchTool(BaseTool):
    name: str = "Search Knowledge Base"
    description: str = "Useful for searching the research documents and internal knowledge base about the topic."

    def _run(self, query: str) -> str:
        # We use a mock config or pass credentials if needed
        config = {"configurable": {"retriever_provider": "chroma", "collection_name": "Research"}}
        from shared.retrieval import make_retriever
        with make_retriever(config) as retriever:
            docs = retriever.invoke(query)
            raw_result = "\n\n".join([f"Source: {d.metadata.get('source', 'Unknown')}\nContent: {d.page_content}" for d in docs])
            
            # --- Prompt Compression Logic ---
            # Compressing search results to save tokens and stay within rate limits
            compressed_result = compress_text(raw_result, query=query)
            
            import time
            time.sleep(5) # Reduced sleep as compression adds its own delay
            return compressed_result if compressed_result else "No relevant information found."

chroma_search_tool = ChromaSearchTool()

class TavilySearchTool(BaseTool):
    name: str = "Tavily Web Search"
    description: str = "Useful for searching the internet for real-time information, news, and technical updates."

    def _run(self, query: str) -> str:
        api_key = os.environ.get("TAVILY_API_KEY")
        if not api_key:
            return "Tavily API key not found. Please set TAVILY_API_KEY in your .env file."
            
        from tavily import TavilyClient
        import os
        
        client = TavilyClient(api_key=api_key)
        # Using advanced search for deeper context
        response = client.search(query=query, search_depth="advanced", max_results=5)
        
        results = response.get('results', [])
        formatted_results = "\n\n".join([
            f"Title: {r.get('title')}\nURL: {r.get('url')}\nContent: {r.get('content')}" 
            for r in results
        ])
        
        # Apply the same compression logic to web results to save tokens
        return compress_text(formatted_results, query=query)

tavily_tool = TavilySearchTool()

# --- Agent Definitions ---

def create_research_crew(topic: str):
    from crewai import LLM
    config = BaseConfiguration()
    
    # 🚀 Tiered Model Architecture from Architectural Blueprint
    # Lead Researcher: Deep intelligence layer with search enabled
    llm_researcher = LLM(model=config.research_model)
    # Senior Content Analyst: Ultra-fast synthesis and complex reasoning (Core)
    llm_analyst = LLM(model=config.core_model)
    # Fact Checker: Fact-checking and grounding
    llm_grounder = LLM(model=config.grounding_model)
    # Final Editor: Fast summarization and fallback
    llm_editor = LLM(model=config.fast_model)

    # 1. Lead Researcher (Deep Intelligence Tier)
    researcher = Agent(
        role='Lead Researcher',
        goal=f'Conduct deep research on {topic} using both internal knowledge and real-time web data.',
        backstory='Expert at finding high-quality information and formulating complex search queries across multiple knowledge layers.',
        tools=[chroma_search_tool, tavily_tool],
        llm=llm_researcher,
        verbose=True,
        allow_delegation=False
    )
    # ... (Rest of the file remains similar)

    # 2. Senior Content Analyst (Core Reasoning Tier)
    analyst = Agent(
        role='Senior Content Analyst',
        goal=f'Analyze the research findings about {topic} and synthesize them into a structured report.',
        backstory='Highly logical thinker who excels at connecting disparate pieces of information and reasoning through complex problems.',
        llm=llm_analyst,
        verbose=True,
        allow_delegation=False
    )

    # 3. Fact Checker (Grounding Tier)
    fact_checker = Agent(
        role='Fact Checker',
        goal='Ensure all claims in the synthesized report are grounded in the provided research data.',
        backstory='Meticulous reviewer who verifies every detail against sources to prevent hallucinations.',
        llm=llm_grounder,
        verbose=True,
        allow_delegation=False
    )

    # 4. Final Editor (Fast/Summary Tier)
    editor = Agent(
        role='Final Editor',
        goal='Refine the report for clarity, conciseness, and impact.',
        backstory='Expert communicator who ensures the final output is sharp and easy to digest.',
        llm=llm_editor,
        verbose=True,
        allow_delegation=False
    )

    # --- Task Definitions ---

    research_task = Task(
        description=f"Thoroughly search the vector database for all information related to {topic}. Focus on key findings and technical data.",
        expected_output="A list of raw findings and source snippets with their respective metadata.",
        agent=researcher
    )

    synthesis_task = Task(
        description=f"Review the raw findings and construct a comprehensive analysis of {topic}. Structure it into clear sections with logical flow.",
        expected_output="A detailed, structured research report draft.",
        agent=analyst,
        context=[research_task]
    )

    validation_task = Task(
        description="Review the report draft and flag any inaccuracies or unverified claims. Contrast the text against the source snippets.",
        expected_output="A list of corrections or a 'Verified' stamp for each section.",
        agent=fact_checker,
        context=[synthesis_task, research_task]
    )

    final_report_task = Task(
        description="Incorporate the fact-checker's feedback and polish the report into a final, professional document.",
        expected_output="A premium, factually accurate, and easy-to-read research report in markdown format.",
        agent=editor,
        context=[validation_task, synthesis_task]
    )

    # --- Assemble the Crew ---

    return Crew(
        agents=[researcher, analyst, fact_checker, editor],
        tasks=[research_task, synthesis_task, validation_task, final_report_task],
        process=Process.sequential,
        verbose=True,
        max_rpm=2 # Correct place for RPM limit in modern CrewAI
    )
