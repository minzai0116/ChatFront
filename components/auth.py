import streamlit as st
from config.settings import USER_CREDENTIALS
from streamlit_oauth import OAuth2Component
import requests

def is_authenticated():
    return st.session_state.get("page") == "chatbot"

def show_login():
    st.markdown("<br><br>", unsafe_allow_html=True)

    # 🎨 로고 정중앙
    col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
    with col_logo2:
        st.image("assets/logo(example).png", width=600)

    st.markdown("## 🙋 아이디로 로그인")
    st.markdown("로그인 정보를 입력해주세요.")

    # 📌 기본 로그인 입력
    username = st.text_input("아이디", placeholder="아이디를 입력하세요")
    password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")

    # ✅ 로그인 버튼
    if st.button("🔐 로그인", use_container_width=True):
        if USER_CREDENTIALS.get(username) == password:
            st.session_state.page = "chatbot"
            st.session_state.username = username
            st.rerun()
        else:
            st.error("❗ 아이디 또는 비밀번호가 올바르지 않습니다.")

    st.markdown("")

    # 📌 회원가입 및 게스트
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 회원가입", use_container_width=True):
            st.session_state.page = "signup"

    with col2:
        if st.button("🤖 로그인 없이 시작", use_container_width=True):
            st.session_state.page = "chatbot"
            st.session_state.username = "guest"
            st.rerun()

    st.markdown("----")
    st.markdown("#### 또는 Google 계정으로 로그인")

    # 🌐 Google OAuth
    oauth2 = OAuth2Component(
        client_id=st.secrets["google"]["client_id"],
        client_secret=st.secrets["google"]["client_secret"],
        authorize_endpoint="https://accounts.google.com/o/oauth2/auth",
        token_endpoint="https://oauth2.googleapis.com/token",
    )

    token = oauth2.authorize_button(
        name="Google 로그인",
        redirect_uri="http://localhost:8501",  # 배포 시 도메인 변경
        scope="https://www.googleapis.com/auth/userinfo.email",
        key="google-login-button",
    )

    if token:
        if "token" in token and "access_token" in token["token"]:
            access_token = token["token"]["access_token"]

            user_info = requests.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            ).json()

            st.session_state.username = user_info.get("email", "google_user")
            st.session_state.page = "chatbot"
            st.success(f"✅ Google 로그인 성공: {st.session_state.username}")
            st.rerun()
        else:
            st.error("Google 로그인 중 문제가 발생했습니다. 다시 시도해주세요.")