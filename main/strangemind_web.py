from al_engine import generate_response  # This pulls your custom AI logic

import streamlit as st

st.set_page_config(page_title="Strangemind AI", layout="centered")

st.title("🧠 Strangemind AI")
st.subheader("Chat with your personalized AI")

prompt = st.text_area("Ask your question:", placeholder="E.g., What’s the meaning of life?")

if st.button("Get Response"):
    if prompt.strip():
        with st.spinner("Thinking like a genius..."):
            try:
                response = generate_response(prompt)
                st.success(response)
            except Exception as e:
                st.error(f"Something broke: {e}")
    else:
        st.warning("Don’t leave it blank. Give your AI something to chew on.")
