import os
from langchain.chains import ConversationalRetrievalChain
from langchain_groq import ChatGroq
from process import load_and_chunk, embed_and_store
import streamlit as st
import json

def get_chat_filename(username: str) -> str:
    safe_username = username.replace(" ", "_")
    return f"chat_sessions_{safe_username}.json"

def save_chats(username: str, chat_sessions: dict):
    filename = get_chat_filename(username)
    with open(filename, "w") as f:
        json.dump(chat_sessions, f)

def load_chats(username: str) -> dict:
    filename = get_chat_filename(username)
    if os.path.exists(filename):
        with open(filename) as f:
            return json.load(f)
        
    return {
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


def process_pdf(uploaded_file):

    os.makedirs("sample_docs", exist_ok=True)
    file_path = f"sample_docs/{uploaded_file.name}"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    chunks = load_and_chunk(file_path)
    db = embed_and_store(chunks)

    llm = ChatGroq(
        temperature=0.2,
        model="llama3-70b-8192"
    )

    retriever = db.as_retriever()
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )

    return qa_chain


def handle_query(chat_session: dict, query: str):
    
    if not chat_session.get("qa_chain"):
        st.warning("Please upload a document first.")
        return
    
    try:
        result = chat_session["qa_chain"].invoke({
            "question": query,
            "chat_history": chat_session["history"]
        })

    except Exception as ex:
        st.error(f"Currently the server is down. Can you try little later")
        return
    
    question_with_file = f"{query} : [File: {chat_session.get("uploaded_file").name}]" # type: ignore
    chat_session["history"].append((question_with_file, result['answer']))

    st.markdown("### Answer")
    st.write(result['answer'])

