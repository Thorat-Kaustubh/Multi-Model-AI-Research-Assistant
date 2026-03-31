import streamlit as st
import os
import sys
import uuid
from typing import List, Dict, Any
from dotenv import load_dotenv
from streamlit_option_menu import option_menu

# Add backend/src to sys.path for local imports
sys.path.append(os.path.join(os.getcwd(), "backend", "src"))

# Lazy imports for performance
from shared.supabase_client import (
    save_chat_history, 
    get_chat_history, 
    get_user_threads
)

# Load environment variables
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="Streamlit AI Assistant",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Corporate Minimalist CSS (Final Calibration) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Source Sans Pro', sans-serif;
        background-color: white !important;
        color: #31333f;
    }
    
    section.main > div {
        max-width: 800px;
        margin: 0 auto;
        padding-top: 50px;
    }
    
    .stChatMessage {
        background-color: transparent !important;
        border: none !important;
        margin-bottom: 0px !important;
    }

    /* Starter Bubbles (Official Look) */
    .starter-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        justify-content: flex-start;
        margin-top: 20px;
    }

    .stButton > button {
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
        background-color: white !important;
        color: #475569 !important;
        font-size: 0.85rem !important;
        padding: 5px 12px !important;
    }

    .stChatInput {
        border-radius: 15px !important;
        background-color: #f1f5f9 !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    .floating-badges {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 999;
        display: flex;
        flex-direction: column;
        gap: 4px;
        text-align: right;
    }
    
    .badge {
        font-size: 0.6rem;
        padding: 2px 8px;
        border-radius: 5px;
        background: #f8fafc;
        color: #94a3b8;
        border: 1px solid #f1f5f9;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State ---
if "user_id" not in st.session_state:
    st.session_state.user_id = "kaustubhthorat07"
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar (Gemini Pro Layout) ---
with st.sidebar:
    st.markdown("<div style='padding: 20px 0 10px 0;'><h2 style='font-size: 1.3rem; font-weight: 600;'>Research Hub</h2></div>", unsafe_allow_html=True)
    
    if st.button("+ New Research", use_container_width=True):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("<div style='color: #94a3b8; font-size: 0.75rem; margin: 20px 0 10px 0; text-transform: uppercase; font-weight: 600;'>Recent Research</div>", unsafe_allow_html=True)
    
    try:
        user_threads = get_user_threads(st.session_state.user_id)
        if user_threads:
            titles = [t["title"] for t in user_threads]
            ids = [t["thread_id"] for t in user_threads]
            current_idx = ids.index(st.session_state.thread_id) if st.session_state.thread_id in ids else 0
            
            selected = option_menu(
                None, titles, 
                icons=['chat-left'] * len(titles), 
                menu_icon="cast", 
                default_index=current_idx,
                styles={
                    "container": {"padding": "0!important", "background-color": "transparent"},
                    "icon": {"color": "#64748b", "font-size": "14px"}, 
                    "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px", "color": "#475569", "--hover-color": "#f8fafc"},
                    "nav-link-selected": {"background-color": "#eff6ff", "color": "#2563eb", "font-weight": "500"},
                }
            )
            
            selected_id = ids[titles.index(selected)]
            if selected_id != st.session_state.thread_id:
                st.session_state.thread_id = selected_id
                st.session_state.messages = []
                st.rerun()
    except Exception:
        pass

# --- History Sync Clean-up ---
if not st.session_state.messages:
    raw_history = get_chat_history(st.session_state.user_id, st.session_state.thread_id)
    if raw_history:
        st.session_state.messages = [{"role": m["role"], "content": m["message"]} for m in raw_history]

# --- Display Content ---
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 40px;">
        <div style="font-size: 60px; margin-bottom: 10px;">⚛️</div>
        <h1 style="font-size: 3rem; font-weight: 700;">Streamlit AI assistant</h1>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,1,1.2])
    with col1:
        if st.button("🛡️ What is Streamlit?", key="p1", use_container_width=True): st.session_state.p = "What is Streamlit?"
    with col2:
        if st.button("💾 Session state", key="p2", use_container_width=True): st.session_state.p = "Help me understand session state"
    with col3:
        if st.button("📈 Interactive charts", key="p3", use_container_width=True): st.session_state.p = "How do I make an interactive chart?"
    
    col4, col5 = st.columns([1, 1.2])
    with col4:
        if st.button("👕 Customize app", key="p4", use_container_width=True): st.session_state.p = "How do I customize my app?"
    with col5:
        if st.button("📦 Deploying at work", key="p5", use_container_width=True): st.session_state.p = "Deploying an app at work"
    
    st.markdown("<br><div style='text-align: left; color: #cbd5e1; font-size: 0.75rem;'>⚖️ Legal disclaimer</div>", unsafe_allow_html=True)
    if (ptr := st.session_state.get("p")):
        prompt = ptr
        del st.session_state["p"]
    else:
        prompt = st.chat_input("Ask a question...")
else:
    prompt = st.chat_input("Ask a question...")

# Message Loop
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "⚛️"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

if prompt:
    # Dedup check
    if not (st.session_state.messages and st.session_state.messages[-1]["content"] == prompt):
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        save_chat_history(st.session_state.user_id, st.session_state.thread_id, prompt, "user")
        
        with st.chat_message("assistant", avatar="⚛️"):
            status = st.status("🌌 Researching...", expanded=False)
            placeholder = st.empty()
            try:
                from research_crew import create_research_crew
                crew = create_research_crew(prompt)
                res = str(crew.kickoff())
                placeholder.markdown(res)
                st.session_state.messages.append({"role": "assistant", "content": res})
                save_chat_history(st.session_state.user_id, st.session_state.thread_id, res, "assistant")
                status.update(label="✅ Complete", state="complete")
            except Exception as e:
                st.error(f"Error: {e}")
                status.update(label="❌ Failed", state="error")

# Floating Badges
st.markdown("""
<div class="floating-badges">
    <div class="badge">Model: Llama 3.3/Gemini 2.0</div>
    <div class="badge">Cloud: Active</div>
</div>
""", unsafe_allow_html=True)
