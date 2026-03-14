import os
import geocoder
from dotenv import load_dotenv
from supabase import create_client

# 1. Load credentials from .env
load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def trigger_shopper_detection(user_id, store_id):
    print(f"🛰️ Agent 1: Scanning for user {user_id}...")
    
    payload = {
        "user_id": user_id,
        "store_id": store_id,
        "status": "location_detected" 
    }
    
    try:
        supabase.table("active_sessions").insert(payload).execute()
        print(f"✅ Success! User {user_id} registered at {store_id}.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # --- GPS Logic ---
    print("📍 Checking your current location...")
    g = geocoder.ip('me') # Gets your GPS via IP (Free)
    current_coords = g.latlng
    print(f"Current GPS: {current_coords}")

    # You can set this to your actual current coordinates for testing!
    # If the user is 'near' these coordinates, trigger the agent.
    trigger_shopper_detection("shopper_nitya_88", "hyderabad_central_mall")