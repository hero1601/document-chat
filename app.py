import streamlit as st
from button import all_button_background
from login import login_top_right
from chat_utils import save_chats, load_chats
from chat_manager import init_chat_state, chat_ui
import copy


st.warning("""
⚠️ **Safari users:** Login may fail to recognize your account due to privacy restrictions.  
For best results, use Chrome or Firefox.

Please sign in at [Google.com](https://google.com) first, then retry here.

You can use the app without logging in, but your data won’t be saved.
""")
st.set_page_config(page_title="Chat with Document")
st.title("📄 Chat with your Document")
all_button_background()

authenticator, name, authentication_status, username = login_top_right()

if authentication_status:
    user_data = load_chats(username) # type: ignore
    init_chat_state(user_data)
else:
    init_chat_state()

chat_ui()

if authentication_status:

    chat_sessions_copy = copy.copy(st.session_state.chat_sessions)
    
    for chat_name, chat_data in chat_sessions_copy.items():
        if chat_data.get("uploaded_file") is not None:
            chat_data["uploaded_file"] = getattr(chat_data["uploaded_file"], "name", None)
        
        # Remove qa_chain before saving
        chat_data["qa_chain"] = None

    user_data_to_save = {
        "chat_tabs": st.session_state.chat_tabs,
        "current_chat": st.session_state.current_chat,
        "previous_chat": st.session_state.previous_chat,
        "chat_sessions": chat_sessions_copy,
    }

    save_chats(username, user_data_to_save)  # type: ignore
