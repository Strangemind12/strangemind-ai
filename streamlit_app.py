import streamlit as st
from supabase import create_client, Client

# Load secrets
ADMIN_PASSWORD = st.secrets["admin_password"]
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]

# Authenticate
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

# Supabase connection
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
