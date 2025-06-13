import os
import streamlit as st

# Load environment variables
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Log what we're loading (don't worry, it won't print secrets)
st.write("🔐 Secrets loaded:",
         {"ADMIN_PASSWORD set?": bool(ADMIN_PASSWORD),
          "SUPABASE_URL set?": bool(SUPABASE_URL),
          "SUPABASE_KEY set?": bool(SUPABASE_KEY)})

if not ADMIN_PASSWORD:
    st.error("❌ ADMIN_PASSWORD not set in environment variables.")
    st.stop()

# Use the password for authentication
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

# Run auth check
if not authenticate():
    st.stop()
