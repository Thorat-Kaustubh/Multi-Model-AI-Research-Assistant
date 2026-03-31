import os
import sys
import chromadb
# from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Add src to sys.path
sys.path.append(os.path.join(os.getcwd(), "backend", "src"))

load_dotenv()

def setup_chroma():
    """Initialize the Chroma Cloud collection."""
    print("🚀 Connecting to Chroma Cloud...")
    
    # Use HttpClient for Chroma Cloud
    try:
        host = os.getenv("CHROMA_HOST", "api.trychroma.com")
        if not host.startswith("http"):
            host = f"https://{host}"
            
        client = chromadb.HttpClient(
            host=host,
            headers={"X-Chroma-Token": str(os.getenv('CHROMA_API_KEY'))},
            tenant=os.getenv("CHROMA_TENANT", "default_tenant"),
            database=os.getenv("CHROMA_DATABASE", "default_database")
        )
    except Exception as e:
        print(f"❌ Error creating Chroma Cloud client: {e}")
        return

    # Create or get the collection
    collection_name = "Research"
    try:
        collection = client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Primary research and knowledge base collection"}
        )
        print(f"✅ Collection '{collection_name}' is ready on Chroma Cloud!")
    except Exception as e:
        print(f"❌ Error creating collection: {e}")

def supabase_sql_instructions():
    """Print instructions for Supabase table creation."""
    print("\n--- 🔗 Supabase SQL Setup ---")
    print("Please run the following SQL command in your Supabase SQL Editor to enable chat history persistence:\n")
    print("""
    CREATE TABLE IF NOT EXISTS chat_history (
      id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
      created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, now()) NOT NULL,
      user_id TEXT NOT NULL,
      message TEXT NOT NULL,
      role TEXT NOT NULL
    );
    """)
    print("----------------------------\n")

if __name__ == "__main__":
    setup_chroma()
    supabase_sql_instructions()
    print("✨ Database setup complete!")
