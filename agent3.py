import os
from dotenv import load_dotenv
from supabase import create_client

# 1. LOAD CONFIGURATION
load_dotenv()  # This reads your .env file
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    print("❌ ERROR: SUPABASE_URL or SUPABASE_KEY not found in .env file!")
    exit()

# 2. INITIALIZE SUPABASE
supabase = create_client(url, key)

def run_stockmaster_agent(user_interests=None):
    """
    Agent 3 Logic: 
    - Filters inventory based on User Interests (from Agent 2).
    - Vetoes items with stock < 5.
    - Promotes items with high stock (> 20) or good margins.
    """
    print("\n🤖 [Agent 3: Stockmaster] Starting analysis...")

    # Fetch data from Supabase
    try:
        response = supabase.table('store_inventory').select("*").execute()
        inventory = response.data
    except Exception as e:
        print(f"❌ Database Error: {e}")
        return []

    approved_deals = []

    for item in inventory:
        name = item['product_name']
        category = item['category']
        stock = item['stock_count']
        cost = item['cost_price']
        price = item['selling_price']
        
        # BUSINESS LOGIC 1: Interest Match
        # If Agent 2 provided tags, we only look at those categories
        if user_interests and category not in user_interests:
            continue

        # BUSINESS LOGIC 2: The 'Veto' (Scarcity check)
        if stock < 5:
            print(f"   ⚠️  VETO: '{name}' - Stock is too low ({stock}). No discount allowed.")
            continue

        # BUSINESS LOGIC 3: The 'Promote' (Opportunity check)
        margin = price - cost
        margin_percent = (margin / price) * 100

        # We promote if we have lots of stock OR if we have a huge profit margin
        if stock > 20 or margin_percent > 30:
            print(f"   ✅ PROMOTE: '{name}' - Stock: {stock}, Margin: {margin_percent:.1f}%")
            
            # Pass this data to the next stage
            approved_deals.append({
                "id": item['id'],
                "name": name,
                "current_price": price,
                "cost_price": cost,
                "stock": stock,
                "reason": "High inventory/High margin"
            })

    print(f"🏁 [Agent 3] Analysis complete. {len(approved_deals)} items approved.\n")
    return approved_deals

# --- TEST BLOCK ---
# You can run this file directly to test it before connecting to the other laptops.
if __name__ == "__main__":
    # Mocking what Agent 2 might send (e.g., ['Dairy', 'Bakery'])
    test_interests = ['Dairy', 'Bakery', 'Vegan'] 
    results = run_stockmaster_agent(test_interests)
    
    print("PROPOSALS FOR NEGOTIATOR:")
    for deal in results:
        print(f"- {deal['name']} @ ${deal['current_price']}")
# --- ADD THIS INSIDE AGENT 3 ---
if results:
    # 1. Update the session with the approved items and the new status
    supabase.table("active_sessions").update({
        "approved_items": results, # Pass the list of 4 items
        "status": "offer_ready"    # THIS WAKES UP AGENT 4
    }).eq("status", "profile_created").execute() 
    
    print("🚀 Data sent to Supabase! Agent 4 should pick it up now.")