import os
import json
import chromadb
from dotenv import load_dotenv

load_dotenv()

def populate_chroma():
    print("🚀 Connecting to Chroma Cloud to populate data...")
    host = os.getenv("CHROMA_HOST", "api.trychroma.com")
    if not host.startswith("http"):
        host = f"https://{host}"
        
    client = chromadb.HttpClient(
        host=host,
        headers={"X-Chroma-Token": str(os.getenv('CHROMA_API_KEY'))},
        tenant=os.getenv("CHROMA_TENANT", "default_tenant"),
        database=os.getenv("CHROMA_DATABASE", "default_database")
    )

    collection = client.get_or_create_collection("Research")
    
    with open("backend/src/sample_docs.json", "r") as f:
        docs = json.load(f)
    
    print(f"Adding {len(docs)} documents to Chroma Cloud...")
    
    ids = [str(i) for i in range(len(docs))]
    documents = [d["page_content"] for d in docs]
    metadatas = [d["metadata"] for d in docs]
    
    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    print("✅ Chroma Cloud is now populated with research knowledge!")

if __name__ == "__main__":
    populate_chroma()
