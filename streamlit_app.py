import streamlit as st
import json
from datetime import datetime
from bot_utils.message_sender import send_reply_to_whatsapp
from streamlit_autorefresh import st_autorefresh

# Auto-refresh every 30 seconds
st_autorefresh(interval=30 * 1000, key="refresh")

# 🔐 DEBUG: Show secrets only if debugging (remove later)
# st.write("DEBUG SECRETS:", st.secrets)

# ✅ Check if secrets are loaded
if "admin_password" not in st.secrets:
    st.error("❌ 'admin_password' is missing from secrets.toml!")
    st.stop()

# ✅ Auth Function (fixes premature stopping)
def authenticate():
    password = st.text_input("Enter admin password:", type="password")
    if password:
        if password == st.secrets["admin_password"]:
            return True
        else:
            st.error("❌ Wrong password.")
            return False
    else:
        return False

if not authenticate():
    st.stop()
