# 🔬 Premium AI Research Assistant (2026)

A state-of-the-art Multi-Model Research Agent powered by **LangGraph**, **ChromaDB**, and **Supabase**. This system orchestrates multiple LLMs (Groq and Google) to perform complex research tasks through a beautiful **Streamlit** dashboard.

## 📁 System Architecture
The project is split into two main sections:

- **`/backend`**: LangGraph-based research logic, model tiers, and retrieval engine.
- **`/frontend`**: Streamlit application UI with premium aesthetics and history tracking.

## 🌈 LLM Orchestration (Multi-Tier)
The system leverages 4 distinct model tiers for optimal performance:
- **Core (Llama 3.3 70B)**: Deep synthesis and complex reasoning.
- **Fast (Llama 3.1 8B)**: Quick query refinement and routing.
- **Grounding (Gemini 2.5 Flash Lite)**: Fact-checking and grounding.
- **Research (Gemini 3.1 Flash Lite)**: Intelligent search-query generation.

## 🛠️ Quick Setup
1. **Initialize Virtual Environment**:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
2. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```
3. **Environment Setup**:
   Copy `.env.example` to `.env` and fill in your API keys.
4. **Run Application**:
   ```powershell
   streamlit run frontend/app.py
   ```

## 🔋 Key Integrations
- **Vector DB**: ChromaDB for local document retrieval.
- **Persistence**: Supabase for cross-conversation chat history.
- **Tracing**: LangSmith support for debugging complex agent flows.
