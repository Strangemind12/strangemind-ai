import os
import streamlit as st
from supabase import create_client, Client

# --- Load password ---
# Priority: st.secrets (local) else env vars (Render)
try:
    ADMIN_PASSWORD = st.secrets["admin_password"]
except Exception:
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# --- Load Supabase config ---
try:
    SUPABASE_URL = st.secrets["supabase"]["url"]
    SUPABASE_KEY = st.secrets["supabase"]["key"]
except Exception:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# --- Debug loaded secrets ---
st.write("🔐 Secrets loaded:",
         {"ADMIN_PASSWORD set?": bool(ADMIN_PASSWORD),
          "SUPABASE_URL set?": bool(SUPABASE_URL),
          "SUPABASE_KEY set?": bool(SUPABASE_KEY)})

if not ADMIN_PASSWORD:
    st.error("❌ Admin password not set! Set it in secrets.toml or environment variables.")
    st.stop()

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("❌ Supabase URL or Key missing! Check your secrets or env vars.")
    st.stop()

# --- Authentication ---
def authenticate():
    password = st.text_input("Enter admin password:", type="password")
    if password == "":
        st.info("🛂 Please enter the admin password to continue.")
        st.stop()
    elif password == ADMIN_PASSWORD:
        st.success("✅ Authenticated")
        return True
    else:
        st.error("❌ Wrong password")
        st.stop()

if not authenticate():
    st.stop()

# --- Connect to Supabase ---
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
st.write("✅ Connected to Supabase")

# --- Step 4: Fetch Messages ---
st.header("📥 Incoming Messages")

messages_response = supabase.table("messages").select("*").order("timestamp", desc=True).limit(10).execute()
messages = messages_response.data

if not messages:
    st.info("No messages yet.")
else:
    for msg in messages:
        st.markdown(f"""
        **Sender Name:** {msg['sender_name']}  
        **Sender ID:** {msg['sender_id']}  
        **Chat Type:** {msg['chat_type']}  
        **Message:** {msg['message']}  
        **Time:** {msg['timestamp']}  
        """)

        # --- Step 5: Insert a Reply ---
        with st.expander(f"💬 Reply to: {msg['sender_name']}"):
            reply_text = st.text_area(f"Write reply to message ID {msg['id']}", key=f"reply_{msg['id']}")
            if st.button(f"Send Reply to {msg['sender_name']}", key=f"btn_{msg['id']}"):
                if reply_text.strip() == "":
                    st.warning("Reply cannot be empty.")
                else:
                    supabase.table("replies").insert({
                        "message_id": msg['id'],
                        "reply_text": reply_text,
                        "replied_by": "admin"
                    }).execute()
                    st.success(f"✅ Reply sent to {msg['sender_name']}!")

        # --- Bonus: Show Replies ---
        reply_res = supabase.table("replies").select("*").eq("message_id", msg['id']).execute()
        replies = reply_res.data
        if replies:
            with st.expander(f"📨 View Replies to: {msg['sender_name']}"):
                for reply in replies:
                    st.markdown(f"""
                    > **Reply:** {reply['reply_text']}  
                    ⏰ {reply['replied_at']} — by *{reply['replied_by']}*
                    """)
