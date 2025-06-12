def authenticate():
    password = st.text_input("Enter admin password:", type="password")
    if password == st.secrets["admin_password"]:
        return True
    else:
        st.stop()

if "admin_password" not in st.secrets:
    st.error("Missing admin password in secrets.toml!")
    st.stop()
