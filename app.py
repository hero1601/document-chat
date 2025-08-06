import streamlit as st
import os
from dotenv import load_dotenv
from chat_utils import process_pdf, handle_query

st.set_page_config(page_title="Chat with Document")
st.title("📄 Chat with your Document")
load_dotenv()
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# --- Initialize chat state map ---
if "chat_tabs" not in st.session_state:
    st.session_state.chat_tabs = ["Chat 1"]
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {
        "Chat 1": {
            "uploaded_file_name": None,
            "qa_chain": None,
            "history": []
        }
    }


if st.sidebar.button("➕ New Chat"):
    new_chat = f"Chat {len(st.session_state.chat_tabs) + 1}"
    st.session_state.chat_tabs.append(new_chat)
    st.session_state.chat_sessions[new_chat] = {
        "uploaded_file_name": None,
        "qa_chain": None,
        "history": []
    }
    st.session_state.current_chat = new_chat

chat_selection = st.sidebar.radio(
    "📁 Chats",
    st.session_state.chat_tabs,
    key="current_chat"
)

chat = st.session_state.chat_sessions[st.session_state.current_chat]
st.subheader(f"🗂️ {st.session_state.current_chat}")

uploaded_file = st.file_uploader("Upload a PDF", type="pdf", key=f"upload_{st.session_state.current_chat}")

if uploaded_file:
    if chat["uploaded_file_name"] != uploaded_file.name:
        chat["uploaded_file_name"] = uploaded_file.name

        with st.spinner("Processing document..."):
            chat["qa_chain"] = process_pdf(uploaded_file)

    # --- Handle QA interaction ---
    if chat["qa_chain"] != None:
        query = st.text_input("Ask a question about the document:", key=f"query_{st.session_state.current_chat}")
        if query:
            handle_query(chat, query)