import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

@st.cache_resource
def get_supabase_client() -> Client:
    """Initialize and return a Supabase client."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        st.warning("Supabase credentials missing. History will not be saved.")
        return None
    
    return create_client(url, key)

def save_chat_history(user_id: str, message: str, role: str):
    """Save a chat message to Supabase."""
    client = get_supabase_client()
    if not client:
        return
    
    try:
        client.table("chat_history").insert({
            "user_id": user_id,
            "message": message,
            "role": role
        }).execute()
    except Exception as e:
        print(f"Error saving to Supabase: {e}")

def get_chat_history(user_id: str):
    """Retrieve chat history from Supabase."""
    client = get_supabase_client()
    if not client:
        return []
    
    try:
        response = client.table("chat_history").select("*").eq("user_id", user_id).order("created_at").execute()
        return response.data
    except Exception as e:
        print(f"Error fetching from Supabase: {e}")
        return []
