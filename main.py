import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

# Load environment variables from .env file
load_dotenv()

# Global Configuration Threshold
# 0.85 means the issues must be roughly 85% semantically identical to flag as a duplicate
DUPLICATE_THRESHOLD = 0.85

def main():
    print("🚀 Initializing AI Duplicate Detection Engine...\n")

   # 1. Validate Environment Secrets
    openai_key = os.getenv("OPENAI_API_KEY")
    pinecone_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME")

    # Explicitly check each variable. Pylance understands this perfectly.
    if not openai_key or not pinecone_key or not index_name:
        print("❌ Error: Missing required configuration environment variables.")
        return

    # 2. Initialize API Clients
    # Because of the explicit check above, Pylance now guarantees these are strings.
    openai_client = OpenAI(api_key=openai_key)
    pc = Pinecone(api_key=pinecone_key)
    pinecone_index = pc.Index(index_name)

    # 3. Data Ingestion (Production Cloud Setup)
    event_path = os.getenv("GITHUB_EVENT_PATH")
    if not event_path:
        print("❌ Error: GITHUB_EVENT_PATH not found. Are we running in GitHub Actions?")
        return

    try:
        with open(event_path, 'r') as file:
            payload = json.load(file)
            
        # GitHub's actual payload structure hides the data inside an 'issue' object
        if "issue" not in payload:
             print("ℹ️ Event is not an issue. Exiting smoothly.")
             return
             
        issue_data = payload["issue"]
        issue_id = f"issue-{issue_data['number']}" 
        issue_title = issue_data["title"]
        raw_body = issue_data["body"]
        if not raw_body:
            print("❌ Error: Issue body is empty.")
            return
            
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"❌ Data Extraction Error: {e}")
        return

    print(f"📋 Processing {issue_id}: '{issue_title}'")

    # 4. Text Sanitization (The Regex Janitor)
    code_block_pattern = r'```[\s\S]*?```'
    clean_body = re.sub(code_block_pattern, "", raw_body)
    
    # 5. Context Engineering & Truncation
    text_to_embed = f"Title: {issue_title} | Description: {clean_body}"
    safe_text = text_to_embed[:4000] 

    # 6. Generate Vector Embeddings
    print("🧠 Computing mathematical vector context...")
    try:
        embedding_response = openai_client.embeddings.create(
            input=safe_text,
            model="text-embedding-3-small"
        )
        issue_vector = embedding_response.data[0].embedding
    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
        return

# 7. Query Database for Nearest Neighbor Match
    print("🔍 Scanning vector memory for existing duplicates...")
    try:
        # CRITICAL FIX: Request top 2 matches in case the #1 match is the issue itself
        query_response = pinecone_index.query(
            vector=issue_vector,
            top_k=2, 
            include_metadata=True
        )
    except Exception as e:
        print(f"❌ Pinecone Query Error: {e}")
        return

    # 8. Threshold Evaluation Logic
    matches = query_response.get("matches", [])
    
    # CRITICAL FIX: Filter out the current issue ID to prevent the "Self-Duplication" edit loop
    filtered_matches = [m for m in matches if m["id"] != issue_id]
    
    if filtered_matches:
        best_match = filtered_matches[0]
        similarity_score = best_match["score"]
        
        # CRITICAL FIX: Safely extract metadata to prevent NoneType crashes
        metadata = best_match.get("metadata") or {}
        matched_title = metadata.get("title", "Unknown Title")

        print(f"\n📊 Highest match score found: {similarity_score:.4f}")

        if similarity_score >= DUPLICATE_THRESHOLD:
            print("🛑 [MATCH FOUND] This issue appears to be a duplicate!")
            print(f"🔗 Matches existing item: {best_match['id']} ('{matched_title}')")
            print("🤖 BOT ACTION: Leave a comment pointing to the original issue and close.")
            return

    # BRANCH B: Unique Issue
    print("✨ [UNIQUE ISSUE] No severe duplicate detected.")
    print("📤 Saving vector coordinates to database memory for future references...")
    # ... (Keep your existing upsert logic here)
    
    try:
        pinecone_index.upsert(vectors=[{
            "id": issue_id,
            "values": issue_vector,
            "metadata": {
                "title": issue_title
            }
        }])
        print("✅ Unique issue successfully registered in memory.")
    except Exception as e:
        print(f"❌ Pinecone Upsert Error: {e}")

if __name__ == "__main__":
    main()  