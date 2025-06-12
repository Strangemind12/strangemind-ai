import os
import streamlit as st
import toml
import json
from datetime import datetime
from bot_utils.message_sender import send_reply_to_whatsapp
from streamlit_autorefresh import st_autorefresh

# ✅ Manually load secrets if st.secrets is empty (Render fallback)
if not st.secrets:
    try:
        with open(".streamlit_secrets.toml", "r") as f:
            secrets = toml.load(f)
            st.secrets = secrets
    except Exception as e:
        st.error(f"❌ Failed to load fallback secrets: {e}")
        st.stop()

# 🔁 Auto-refresh every 30 seconds
st_autorefresh(interval=30 * 1000, key="refresh")

# ========== AUTH CHECK ==========
if "admin_password" not in st.secrets:
    st.error("❌ 'admin_password' is missing from secrets!")
    st.stop()

def authenticate():
    password = st.text_input("Enter admin password:", type="password")
    if password == st.secrets["admin_password"]:
        return True
    else:
        st.error("❌ Wrong password")
        st.stop()

if not authenticate():
    st.stop()

# ========== LOAD LOGS ==========
def load_message_logs():
    try:
        with open("logs/messages.json", "r") as f:
            return json.load(f)
    except:
        return []

# ========== UI ==========
st.title("📡 Strangemind AI Admin Dashboard")
st.caption("Monitor and reply to user/group messages via WhatsApp.")

logs = load_message_logs()

for msg in logs:
    with st.expander(f"[{msg['timestamp']}] {msg['sender_name']}"):
        st.markdown(
            f"**From:** `{msg['sender_name']}`  \n"
            f"**Chat Type:** `{msg['chat_type']}`  \n"
            f"**Message:** `{msg['message']}`"
        )

        reply = st.text_area(f"Reply to {msg['sender_name']}:", key=f"reply_{msg['id']}")
        if st.button("Send Reply", key=f"send_{msg['id']}"):
            if reply.strip():
                send_reply_to_whatsapp(msg['sender_id'], reply)
                st.success("✅ Reply sent!")
            else:
                st.warning("⚠️ Message is empty.")
