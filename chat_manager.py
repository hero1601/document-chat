from dotenv import load_dotenv
import streamlit as st
from chat_utils import process_pdf, handle_query

load_dotenv()

def init_chat_state(defaults=None):
    if defaults is None:
        defaults = {
            "chat_tabs": ["Chat 1"],
            "current_chat": "Chat 1",
            "previous_chat": "Chat -1",
            "chat_sessions": {
                "Chat 1": {
                    "uploaded_file": None,
                    "qa_chain": None,
                    "history": [],
                }
            },
        }

    if "chat_tabs" not in st.session_state:
        st.session_state.chat_tabs = defaults.get("chat_tabs", ["Chat 1"])
    if "current_chat" not in st.session_state:
        st.session_state.current_chat = defaults.get("current_chat", "Chat 1")
    if "previous_chat" not in st.session_state:
        st.session_state.previous_chat = defaults.get("previous_chat", "Chat -1")
    if "chat_sessions" not in st.session_state:
        st.session_state.chat_sessions = defaults.get("chat_sessions", {
            "Chat 1": {
                "uploaded_file": None,
                "qa_chain": None,
                "history": [],
            }
        })


def chat_ui():
    # New chat button
    if st.sidebar.button("➕ New Chat"):
        new_chat = f"Chat {len(st.session_state.chat_tabs) + 1}"
        st.session_state.chat_tabs.append(new_chat)
        st.session_state.chat_sessions[new_chat] = {
            "uploaded_file": None,
            "qa_chain": None,
            "history": [],
        }
        st.session_state.current_chat = new_chat

    # Chat selection
    chat_selection = st.sidebar.radio(
        "📁 Chats",
        st.session_state.chat_tabs,
        key="current_chat"
    )

    chat = st.session_state.chat_sessions[st.session_state.current_chat]
    st.subheader(f"🗂️ {st.session_state.current_chat}")

    uploaded_file = st.file_uploader("Upload a PDF", type="pdf", key=f"upload_{st.session_state.current_chat}")

    if uploaded_file is None and chat["uploaded_file"] is not None and st.session_state.previous_chat != st.session_state.current_chat:
        uploaded_file = chat["uploaded_file"]
        st.info(f"Using previously uploaded file: {uploaded_file}")

    st.session_state.previous_chat = st.session_state.current_chat

    if uploaded_file is not None:
        if chat["uploaded_file"] != uploaded_file:
            chat["uploaded_file"] = uploaded_file
            with st.spinner("Processing document..."):
                chat["qa_chain"] = process_pdf(uploaded_file)
        
        if chat["qa_chain"] is None:
            chat["qa_chain"] = process_pdf(uploaded_file)

        if chat["qa_chain"] is not None:
            query = st.text_input("Ask a question about the document:", key=f"query_{st.session_state.current_chat}")
            if query:
                handle_query(chat, query)

            with st.expander("🕒 Chat History"):
                for i, (q, a) in enumerate(chat["history"]):
                    st.markdown(f"**Q{i+1}:** {q}")
                    st.markdown(f"**A{i+1}:** {a}")
