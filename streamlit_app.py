import streamlit as st

def authenticate():
    password = st.text_input("Enter admin password:", type="password")
    if password == st.secrets["admin_password"]:
        return True
    else:
        st.warning("❌ Wrong password")
        st.stop()

if "admin_password" not in st.secrets:
    st.error("❌ admin_password is missing from secrets.toml!")
    st.stop()

if not authenticate():
    st.stop()
