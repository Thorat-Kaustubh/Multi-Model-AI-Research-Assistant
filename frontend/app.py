import streamlit as st
import asyncio
import os
import sys
import uuid
from typing import List, Dict, Any
from dotenv import load_dotenv

# Add backend/src to sys.path for local imports
sys.path.append(os.path.join(os.getcwd(), "backend", "src"))

# Import our custom components
from shared.supabase_client import save_chat_history, get_chat_history
from retrieval_graph.graph import graph
from langchain_core.messages import HumanMessage, AIMessage

# Load environment variables
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="Multi-Model AI Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Premium Aesthetics (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }
    
    .stChatFloatingInputContainer {
        background-color: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
    }
    
    .stChatMessage {
        background-color: rgba(51, 65, 85, 0.5);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    .sidebar .sidebar-content {
        background-color: #1e293b;
    }
    
    h1, h2, h3 {
        color: #60a5fa !important;
        font-weight: 600;
    }
    
    .model-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }
    
    .tier-badge {
        font-size: 0.7rem;
        padding: 2px 8px;
        border-radius: 10px;
        text-transform: uppercase;
        font-weight: bold;
    }
    
    .tier-core { background-color: #3b82f6; color: white; }
    .tier-fast { background-color: #10b981; color: white; }
    .tier-grounding { background-color: #f59e0b; color: white; }
    .tier-research { background-color: #8b5cf6; color: white; }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "user_id" not in st.session_state:
    st.session_state.user_id = "default_user" # In a real app, this would be from Auth

# Load history from Supabase on start
if not st.session_state.messages:
    history = get_chat_history(st.session_state.user_id)
    if history:
        for msg in history:
            role = "user" if msg["role"] == "user" else "assistant"
            st.session_state.messages.append({"role": role, "content": msg["message"]})

# --- Sidebar ---
with st.sidebar:
    st.title("🔬 Research Hub")
    st.markdown("---")
    
    st.subheader("Model Tiers")
    
    # Display the LLM Model tiers as per the user's image
    st.markdown("""
    <div class="model-card">
        <span class="tier-badge tier-core">Core</span>
        <div style="font-size: 0.9rem; margin-top: 5px;"><b>Llama 3.3 70B</b></div>
        <div style="font-size: 0.7rem; color: #94a3b8;">Provider: Groq | Purpose: Reasoning</div>
    </div>
    <div class="model-card">
        <span class="tier-badge tier-fast">Fast</span>
        <div style="font-size: 0.9rem; margin-top: 5px;"><b>Llama 3.1 8B</b></div>
        <div style="font-size: 0.7rem; color: #94a3b8;">Provider: Groq | Purpose: Summary</div>
    </div>
    <div class="model-card">
        <span class="tier-badge tier-grounding">Grounding</span>
        <div style="font-size: 0.9rem; margin-top: 5px;"><b>Gemini 2.5 Flash Lite</b></div>
        <div style="font-size: 0.7rem; color: #94a3b8;">Provider: Google | Purpose: Fact-checking</div>
    </div>
    <div class="model-card">
        <span class="tier-badge tier-research">Research</span>
        <div style="font-size: 0.9rem; margin-top: 5px;"><b>Gemini 3.1 Flash Lite</b></div>
        <div style="font-size: 0.7rem; color: #94a3b8;">Provider: Google | Purpose: Deep Intelligence</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("Vector Database")
    st.info("🟢 ChromaDB Active")
    
    st.subheader("Storage")
    st.success("🟢 Supabase Connected")
    
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

# --- Main Interface ---
st.title("Multi-Model Research Assistant")
st.caption("Powered by LangGraph, ChromaDB, and Supabase")

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask a research question..."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to session state
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Save to Supabase
    save_chat_history(st.session_state.user_id, prompt, "user")

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Prepare graph input
        inputs = {"messages": [HumanMessage(content=prompt)]}
        config = {
            "configurable": {
                "thread_id": st.session_state.thread_id,
                "retriever_provider": "chroma"
            }
        }
        
        # Invoke agent
        async def run_agent():
            nonlocal full_response
            try:
                # We use stream for better UX
                async for event in graph.astream(inputs, config=config, stream_mode="values"):
                    if "messages" in event:
                        last_message = event["messages"][-1]
                        if isinstance(last_message, AIMessage):
                            full_response = last_message.content
                            message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                return full_response
            except Exception as e:
                st.error(f"Error invoking agent: {e}")
                return "I'm sorry, I encountered an error while processing your request."

        # Run the async agent
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        full_response = loop.run_until_complete(run_agent())
        
        # Add assistant response to session state
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
        # Save to Supabase
        save_chat_history(st.session_state.user_id, full_response, "assistant")

# --- Footer ---
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #94a3b8; font-size: 0.8rem;'>"
    "Built with Premium AI Research Stack | 2026"
    "</div>", 
    unsafe_allow_html=True
)
