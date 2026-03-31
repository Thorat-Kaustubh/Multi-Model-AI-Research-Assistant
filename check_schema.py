import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(url, key)

try:
    # Try to fetch one row and see the columns
    response = supabase.table("chat_history").select("*").limit(1).execute()
    if response.data:
        print("Columns in chat_history:", response.data[0].keys())
    else:
        print("Table is empty. Cannot determine columns easily from select.")
        # Alternatively, try to insert with thread_id and see what happens
        test_data = {
            "user_id": "schema_test",
            "message": "Testing for thread_id column",
            "role": "system",
            "thread_id": "test_thread"
        }
        try:
            supabase.table("chat_history").insert(test_data).execute()
            print("Successfully inserted with thread_id! Column exists.")
        except Exception as e:
            print(f"Error inserting with thread_id: {e}")
except Exception as e:
    print(f"Error checking schema: {e}")
