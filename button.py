import streamlit as st

def all_button_background():
    st.markdown(
        """
        <style>
        div.stButton > button:first-child {
            background-color: #1a73e8;  /* Google Blue */
            color: white;
            border-radius: 5px;
            height: 3em;
            font-size: 16px;
        }
        div.stButton > button:first-child:hover {
            background-color: #1669c1;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )