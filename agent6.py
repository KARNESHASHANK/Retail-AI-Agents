import os
import time
from dotenv import load_dotenv
from supabase import create_client
from groq import Groq

# 1. Load credentials
load_dotenv()

# 2. Setup Supabase
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

# 3. Setup Groq
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def run_learning_session():
    print("\n🧠 Agent 6: Analyzing data to improve the system...")
    
    # Fetch all data to see what worked and what didn't
    response = supabase.table("active_sessions").select("*").execute()
    all_sessions = response.data

    if not all_sessions:
        print("📭 Not enough data to learn from yet.")
        return

    # Prepare a summary for Groq
    summary = []
    for s in all_sessions:
        status = s.get('status')
        dna = s.get('user_dna', 'Unknown')
        pitch = s.get('pitch', 'No pitch')
        summary.append(f"DNA: {dna} | Status: {status} | Pitch: {pitch}")

    # Ask Groq to find the winning pattern
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a Machine Learning Optimizer. Analyze retail data and provide 1 specific 'Learned Insight' to improve sales."
                },
                {
                    "role": "user",
                    "content": f"Here are the recent sessions: {summary}. Which DNA types bought the most, and how should Agent 4 change its pitch to be more effective?",
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        
        insight = chat_completion.choices[0].message.content
        print(f"✨ LEARNING COMPLETE. Insight for the store owner:\n{insight}")

        # (Optional) You could save this insight to a new table called 'insights' 
        # for the Store Owner's dashboard.
        
    except Exception as e:
        print(f"❌ Error during learning cycle: {e}")

if __name__ == "__main__":
    # In a real system, this runs once an hour or after every 10 purchases
    run_learning_session()