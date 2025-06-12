import streamlit as st
import json
import os
from datetime import datetime
from bot_utils.message_sender import send_reply_to_whatsapp

from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=30 * 1000, key="refresh")

# 🔍 TEMP DEBUG: Check secrets
try:
    st.write("🔐 Loaded secrets:", st.secrets)
except Exception as e:
    st.error(f"❌ Failed to load secrets: {e}")
    st.stop()

# ✅ Now check if the key exists
if "admin_password" not in st.secrets:
    st.error("❌ 'admin_password' is missing from secrets.toml!")
    st.stop()

# ✅ Proceed to password auth
def authenticate():
    password = st.text_input("Enter admin password:", type="password")
    if password == st.secrets["admin_password"]:
        return True
    else:
        st.stop()

if not authenticate():
    st.stop()
