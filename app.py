import streamlit as st
from src.llm import new_chat

st.set_page_config(page_title="Sales Assistant", page_icon="📊")
st.title("Sales Assistant")
st.caption("Ask about top products, stores, trends and forecasts.")

if "chat" not in st.session_state:
    st.session_state.chat = new_chat()
    st.session_state.history = []

with st.sidebar:
    st.subheader("Try asking")
    for ex in ["Top 5 products by revenue",
               "Which stores have the lowest profit margin?",
               "Revenue by region by quarter",
               "Forecast revenue for the next 3 months"]:
        if st.button(ex):
            st.session_state.pending = ex
    if st.button("Clear chat"):
        st.session_state.chat = new_chat()
        st.session_state.history = []
        st.rerun()

for role, text in st.session_state.history:
    st.chat_message(role).write(text)

q = st.chat_input("Ask a question about your data...") or st.session_state.pop("pending", None)
if q:
    st.chat_message("user").write(q)
    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            try:
                ans = st.session_state.chat.send_message(q).text
            except Exception as e:
                ans = f"Sorry, something went wrong: {e}"
        st.write(ans)
    st.session_state.history += [("user", q), ("assistant", ans)]