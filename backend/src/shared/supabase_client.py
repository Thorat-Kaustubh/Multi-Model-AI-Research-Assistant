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
        return None
    
    return create_client(url, key)

def save_chat_history(user_id: str, thread_id: str, message: str, role: str):
    """Save a chat message to Supabase."""
    client = get_supabase_client()
    if not client:
        return
    
    try:
        client.table("chat_history").insert({
            "user_id": user_id,
            "thread_id": thread_id,
            "message": message,
            "role": role
        }).execute()
    except Exception as e:
        print(f"Error saving to Supabase: {e}")

def get_chat_history(user_id: str, thread_id: str):
    """Retrieve chat history from Supabase for a specific thread."""
    client = get_supabase_client()
    if not client:
        return []
    
    try:
        response = client.table("chat_history").select("*").eq("user_id", user_id).eq("thread_id", thread_id).order("created_at").execute()
        return response.data
    except Exception as e:
        print(f"Error fetching from Supabase: {e}")
        return []

def get_user_threads(user_id: str):
    """Retrieve a list of unique threads (sessions) for a specific user."""
    client = get_supabase_client()
    if not client:
        return []
    
    try:
        # Fetch the first user message of each thread to use as a title
        response = client.table("chat_history").select("thread_id, message, created_at").eq("user_id", user_id).eq("role", "user").order("created_at", desc=True).execute()
        
        unique_threads = []
        seen_ids = set()
        for item in response.data:
            if item["thread_id"] not in seen_ids:
                unique_threads.append({
                    "thread_id": item["thread_id"],
                    "title": item["message"][:30] + "..." if len(item["message"]) > 30 else item["message"]
                })
                seen_ids.add(item["thread_id"])
        return unique_threads
    except Exception as e:
        print(f"Error fetching threads: {e}")
        return []

def update_table_schema_sql():
    """Returns the SQL to run in Supabase for the new schema."""
    return """
    ALTER TABLE chat_history ADD COLUMN IF NOT EXISTS thread_id TEXT DEFAULT 'default_thread';
    CREATE INDEX IF NOT EXISTS idx_chat_history_thread_group ON chat_history(user_id, thread_id);
    """
