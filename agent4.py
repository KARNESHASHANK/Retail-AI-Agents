import os
import time
from dotenv import load_dotenv
from supabase import create_client
from groq import Groq

# 1. Load credentials
load_dotenv()

# 2. Setup Supabase
# Ensure these variables are in your .env file
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

# 3. Setup Groq (using Llama 3.3)
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def create_personalized_deal(session_id, user_id, user_dna, approved_items):
    print(f"\n🤝 Agent 4: Crafting deal for user {user_id}...")
    
    # Check if approved_items is a list and has data
    if not approved_items or not isinstance(approved_items, list):
        print("⚠️ No items to process. Skipping...")
        return

    # Fix: Using .get() to avoid KeyErrors if 'name' or 'category' is missing
    try:
        items_list = ", ".join([
            f"{i.get('name', 'Product')} ({i.get('category', 'Retail')})" 
            for i in approved_items
        ])
    except Exception as e:
        print(f"❌ Error formatting items: {e}")
        return
    
    # The Sales Pitch Prompt
    prompt = f"""
    You are a charismatic retail salesman. 
    The shopper's DNA profile is: {user_dna}
    We have these items approved for a deal: {items_list}
    
    Task: Write a short, persuasive sales pitch (max 2 sentences) offering a 15% discount.
    Reference their 'DNA' profile to make it feel special.
    End the message with: 'Use code: DEAL15'
    """

    try:
        # Talk to Groq
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a friendly, high-energy retail assistant. Keep it short."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        
        pitch = chat_completion.choices[0].message.content
        print(f"✨ Pitch Generated: {pitch}")

        # 4. Update Supabase
        # Make sure you have a 'pitch' column (type: text) in your table
        supabase.table("active_sessions").update({
            "pitch": pitch,
            "discount_code": "DEAL15",
            "status": "completed" # Marks the end of the AI pipeline
        }).eq("id", session_id).execute()
        
        print(f"✅ Deal published to Supabase. Session {session_id} is COMPLETE.")

    except Exception as e:
        print(f"❌ Error talking to Groq or updating DB: {e}")

if __name__ == "__main__":
    print("💰 Agent 4 (Negotiator) is LIVE and waiting for 'offer_ready' status...")
    
    while True:
        try:
            # Poll the database for sessions ready for a deal
            response = supabase.table("active_sessions").select("*").eq("status", "offer_ready").execute()
            
            for session in response.data:
                create_personalized_deal(
                    session['id'], 
                    session.get('user_id', 'Unknown'), 
                    session.get('user_dna', 'Valued Shopper'), 
                    session.get('approved_items', [])
                )
        except Exception as e:
            print(f"📡 Connection Error: {e}")
            
        time.sleep(5) # Wait 5 seconds before checking again