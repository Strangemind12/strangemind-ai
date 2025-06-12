from supabase import create_client
import streamlit as st

# Load Supabase creds from secrets
supabase_url = st.secrets["supabase"]["url"]
supabase_key = st.secrets["supabase"]["key"]
supabase = create_client(supabase_url, supabase_key)

def log_to_supabase(sender_id, sender_name, message, chat_type="user"):
    data = {
        "sender_id": sender_id,
        "sender_name": sender_name,
        "message": message,
        "chat_type": chat_type
    }
    try:
        response = supabase.table("logs").insert(data).execute()
        print("✅ Logged to Supabase:", response)
        return True
    except Exception as e:
        print("❌ Failed to log to Supabase:", e)
        return False
