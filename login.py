import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
import os
from urllib.parse import urlencode

# --- OAuth client setup ---
def get_oauth_client():
    CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    REDIRECT_URI = os.getenv("REDIRECT_URI")

    return OAuth2Session(
        CLIENT_ID,
        CLIENT_SECRET,
        scope="openid email profile",
        redirect_uri=REDIRECT_URI
    )

# --- UI helpers ---
def render_login_button(auth_url):
    login_link = f'''
        <a href="{auth_url}" target="_self" style="
            background:#4285F4;
            color:white;
            padding:10px 20px;
            border-radius:4px;
            text-decoration:none;
            font-weight:bold;
            display:inline-block;
        ">Login with Google</a>
    '''
    st.markdown(login_link, unsafe_allow_html=True)
        


def render_logout_button(name):
    st.markdown(f"Hi, {name} ")
    if st.button("Logout"):
        st.session_state.pop("user_info", None)


def handle_oauth_callback(oauth, token_url, userinfo_url):
    params = st.query_params
    if "code" in params:
        query_string = urlencode(params, doseq=True)
        full_url = f"{os.getenv('REDIRECT_URI')}?{query_string}"

        token = oauth.fetch_token(
            token_url,
            authorization_response=full_url,
            redirect_uri=os.getenv("REDIRECT_URI")
        )
        user_info = oauth.get(userinfo_url).json()
        st.session_state["user_info"] = user_info
        st.query_params.clear()
        st.rerun()

# --- Main login UI ---
def login_top_right():
    oauth = get_oauth_client()

    AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USERINFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"

    handle_oauth_callback(oauth, TOKEN_URL, USERINFO_URL)

    authentication_status = False
    username = None
    name = None

    if "user_info" not in st.session_state:
        auth_url, _ = oauth.create_authorization_url(AUTH_URL)
        render_login_button(auth_url)
        
    else:
        user_info = st.session_state["user_info"]
        name = user_info.get("name")
        username = user_info.get("email")
        authentication_status = True
        render_logout_button(name)

    return None, name, authentication_status, username