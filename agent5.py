import os
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

# Email Configuration (Add these to your .env file)
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")  # Your Gmail
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")  # Your App Password

def send_real_email(receiver_email, pitch, discount_code):
    """Sends a real email using SMTP"""
    subject = "🎁 Exclusive Offer Just for You!"
    body = f"""
    Hello!
    
    {pitch}
    
    Use your exclusive code: {discount_code}
    
    See you at the store!
    """

    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connecting to Gmail's SMTP server
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls() # Secure the connection
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
            print(f"📧 Email sent successfully to {receiver_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

def send_proximity_alert(user_id, pitch, discount_code):
    print(f"\n🚨 ALERTING USER: {user_id}")
    
    # Assuming user_id is the user's email address in your table
    send_real_email(user_id, pitch, discount_code)

if __name__ == "__main__":
    print("🔔 Agent 5 (Alert Dispatcher) is LIVE...")
    while True:
        response = supabase.table("active_sessions").select("*").eq("status", "completed").execute()
        
        for session in response.data:
            send_proximity_alert(
                session['user_id'], 
                session.get('pitch', 'Special offer inside!'), 
                session.get('discount_code', 'SAVE15')
            )
            
            supabase.table("active_sessions").update({
                "status": "alert_sent"
            }).eq("id", session['id']).execute()
            
        time.sleep(5)