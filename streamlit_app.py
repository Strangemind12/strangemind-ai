import streamlit as st
import json
import os
from datetime import datetime
from bot_utils.message_sender import send_reply_to_whatsapp  # 👈 Your real send function

# Auto-refresh every 30 seconds
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=30 * 1000, key="refresh")

# ========== Auth ================
def authenticate():
    password = st.text_input("Enter admin password:", type="password")
    if password == st.secrets["admin_password"]:
        return True
    else:
        st.stop()

if "admin_password" not in st.secrets:
    st.error("Missing admin password in secrets.toml!")
    st.stop()

if not authenticate():
    st.stop()

# ========== Load Logs ================
def load_message_logs():
    try:
        with open("logs/messages.json", "r") as f:
            return json.load(f)
    except:
        return []

# ========== UI ================
st.title("📡 Strangemind AI Admin Dashboard")
st.caption("Monitor and reply to user/group messages via WhatsApp.")

logs = load_message_logs()

for msg in logs:
    with st.expander(f"[{msg['timestamp']}] {msg['sender_name']}"):
        st.markdown(f"**From:** `{msg['sender_name']}`  \n"
                    f"**Chat Type:** `{msg['chat_type']}`  \n"
                    f"**Message:** `{msg['message']}`")

        reply = st.text_area(f"Reply to {msg['sender_name']}:", key=f"reply_{msg['id']}")
        if st.button("Send Reply", key=f"send_{msg['id']}"):
            if reply.strip():
                send_reply_to_whatsapp(msg['sender_id'], reply)
                st.success("✅ Reply sent!")
            else:
                st.warning("⚠️ Message is empty.")
