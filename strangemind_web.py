import streamlit as st
from al_engine import generate_response  # Make sure this exists and works

st.set_page_config(page_title="🧠 Strangemind AI", page_icon="🤖")
st.title("🧠 Strangemind AI - Web Interface")

st.markdown("Talk to your AI assistant directly here. No WhatsApp? No problem.")

user_input = st.text_input("You:", "")

if st.button("Send") or user_input:
    with st.spinner("Strangemind is thinking..."):
        try:
            response = generate_response(user_input)
            st.success(response)
        except Exception as e:
            st.error(f"Error: {e}")
