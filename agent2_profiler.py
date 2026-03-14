import os
import time
from dotenv import load_dotenv
from supabase import create_client
from groq import Groq # Using the Groq library from your screenshot

# 1. Load credentials
load_dotenv()

# 2. Setup Supabase
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

# 3. Setup Groq (The one from your screenshot)
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def analyze_shopper_dna(user_id, session_id):
    print(f"\n🧠 Agent 2: Analyzing history for user: {user_id}...")
    
    # Fetch user's past purchases
    history = supabase.table("purchase_history").select("*").eq("user_id", user_id).execute()
    
    if not history.data:
        history_summary = "New shopper, no history."
    else:
        items = [f"{item['item_name']} ({item['category']})" for item in history.data]
        history_summary = ", ".join(items)

    print(f"📋 Found History: {history_summary}")

    # Ask Groq (Llama 3) for the DNA
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a retail psychologist. Define the shopper's DNA in 5 words or less."
                },
                {
                    "role": "user",
                    "content": f"Analyze this history: {history_summary}",
                }
            ],
            model="llama-3.3-70b-versatile", # This is the best free model on Groq
        )
        
        dna_result = chat_completion.choices[0].message.content
        print(f"✨ Groq's Insight: {dna_result}")

        # Update Supabase
        supabase.table("active_sessions").update({
            "user_dna": dna_result,
            "status": "profile_created"
        }).eq("id", session_id).execute()
        
        print(f"✅ DNA saved. Agent 2 work complete.")

    except Exception as e:
        print(f"❌ Error talking to Groq: {e}")

if __name__ == "__main__":
    print("📡 Agent 2 (Groq) is LIVE and listening...")
    while True:
        new_sessions = supabase.table("active_sessions").select("*").eq("status", "location_detected").execute()
        for session in new_sessions.data:
            analyze_shopper_dna(session['user_id'], session['id'])
        time.sleep(5)