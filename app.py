import streamlit as st
from chat import stream_answer

st.set_page_config(page_title="IronStore Assistant", page_icon="💬")
st.title("IronStore Assistant")

# Keep the conversation while the page is open
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show the earlier messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# The input box at the bottom
question = st.chat_input("Ask about a policy or procedure...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching documents..."):
            reply = st.write_stream(stream_answer(question))

    st.session_state.messages.append({"role": "assistant", "content": reply})