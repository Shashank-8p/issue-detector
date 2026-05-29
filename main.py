import os
import json
import re
import requests 
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

load_dotenv()
DUPLICATE_THRESHOLD = 0.65

# NEW FUNCTION: Give the bot hands
def close_duplicate_issue(repo, current_issue_num, matched_issue_num, token):
    url = f"https://api.github.com/repos/{repo}/issues/{current_issue_num}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # 1. Post the explanatory comment
    comment_url = f"{url}/comments"
    comment_body = {
        "body": f"🤖 **AI Duplicate Detector**\n\nI have detected that this issue is a duplicate of #{matched_issue_num}. I am automatically closing this to keep the project backlog clean!"
    }
    requests.post(comment_url, headers=headers, json=comment_body)
    
    # 2. Close the issue
    close_data = {"state": "closed"}
    requests.patch(url, headers=headers, json=close_data)
    print("✅ Issue successfully commented on and closed via API.")

def main():
    print("🚀 Initializing AI Duplicate Detection Engine...\n")

    # Fetch standard secrets plus the new GitHub Token and Repository Name
    openai_key = os.getenv("OPENAI_API_KEY")
    pinecone_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME")
    github_token = os.getenv("GITHUB_TOKEN")
    github_repo = os.getenv("GITHUB_REPOSITORY") # Automatically provided by GitHub Actions

    if not openai_key or not pinecone_key or not index_name:
        print("❌ Error: Missing required configuration environment variables.")
        return

    openai_client = OpenAI(api_key=openai_key)
    pc = Pinecone(api_key=pinecone_key)
    pinecone_index = pc.Index(index_name)

    event_path = os.getenv("GITHUB_EVENT_PATH")
    if not event_path:
        print("❌ Error: GITHUB_EVENT_PATH not found.")
        return

    try:
        with open(event_path, 'r') as file:
            payload = json.load(file)
            
        if "issue" not in payload:
             print("ℹ️ Event is not an issue. Exiting smoothly.")
             return
             
        issue_data = payload["issue"]
        current_issue_number = issue_data['number']
        issue_id = f"issue-{current_issue_number}" 
        issue_title = issue_data["title"]
        raw_body = issue_data["body"]
        
    except Exception as e:
        print(f"❌ Data Extraction Error: {e}")
        return

    print(f"📋 Processing {issue_id}: '{issue_title}'")

    code_block_pattern = r'```[\s\S]*?```'
    clean_body = re.sub(code_block_pattern, "", raw_body) if raw_body else ""
    text_to_embed = f"Title: {issue_title} | Description: {clean_body}"
    safe_text = text_to_embed[:4000] 

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

    print("🔍 Scanning vector memory for existing duplicates...")
    try:
        query_response = pinecone_index.query(vector=issue_vector, top_k=2, include_metadata=True)
    except Exception as e:
        print(f"❌ Pinecone Query Error: {e}")
        return

    matches = query_response.get("matches", [])
    filtered_matches = [m for m in matches if m["id"] != issue_id]
    
    if filtered_matches:
        best_match = filtered_matches[0]
        similarity_score = best_match["score"]
        metadata = best_match.get("metadata") or {}
        matched_title = metadata.get("title", "Unknown Title")
        
        # Extract the integer number from the matched ID (e.g., "issue-1" -> "1")
        matched_issue_number = best_match['id'].split('-')[1]

        print(f"\n📊 Highest match score found: {similarity_score:.4f}")

        if similarity_score >= DUPLICATE_THRESHOLD:
            print("🛑 [MATCH FOUND] This issue appears to be a duplicate!")
            print(f"🔗 Matches existing item: {best_match['id']} ('{matched_title}')")
            
            # TRIGGER THE NEW BOT HANDS!
            if github_token and github_repo:
                close_duplicate_issue(github_repo, current_issue_number, matched_issue_number, github_token)
            else:
                print("⚠️ Skipping API closure: GITHUB_TOKEN or GITHUB_REPOSITORY missing.")
            return

    print("✨ [UNIQUE ISSUE] No severe duplicate detected.")
    print("📤 Saving vector coordinates to database memory for future references...")
    try:
        pinecone_index.upsert(vectors=[{
            "id": issue_id,
            "values": issue_vector,
            "metadata": {"title": issue_title}
        }])
        print("✅ Unique issue successfully registered in memory.")
    except Exception as e:
        print(f"❌ Pinecone Upsert Error: {e}")

if __name__ == "__main__":
    main()