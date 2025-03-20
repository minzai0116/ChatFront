import streamlit as st

# 사이드바 비활성화 설정 (앱의 첫 줄에 위치해야 합니다)
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")  # 사이드바 숨기기

# CSS 파일 경로
css_path = 'style.css'  # style.css 파일 경로 (chatbot.py와 동일한 경로)

# CSS 파일을 불러와서 적용하기
with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 네비게이션 바 HTML (chatbot과 user_info만 추가)
st.markdown("""
    <div class="navbar">
        <a href="chatbot" target="_self">Chatbot</a>
        <a href="user_info" target="_self">User Info</a>
    </div>
""", unsafe_allow_html=True)

# User Information 페이지 내용
st.subheader("User Information Page")

# 사용자 정보 입력 폼
user_name = st.text_input("이름을 입력하세요:")
user_email = st.text_input("이메일을 입력하세요:")
user_age = st.number_input("나이를 입력하세요:", min_value=1, max_value=120)
user_personality = st.selectbox("Choose your personality:", ["외향적", "내향적", "분석적", "감성적"])

# 성격 정보 저장
if st.button("Save Info"):
    if user_name and user_email:
        st.session_state.user_info = {
            "name": user_name,
            "email": user_email,
            "age": user_age,
            "personality": user_personality  # 성격 정보를 세션 상태에 저장
        }
        st.success("User information saved successfully!")
    else:
        st.error("Please fill in all the fields.")


# 저장된 사용자 정보 표시
if "user_info" in st.session_state:
    st.subheader("저장된 정보")
    st.write(f"이름: {st.session_state.user_info['name']}")
    st.write(f"이메일: {st.session_state.user_info['email']}")
    st.write(f"나이: {st.session_state.user_info['age']}")
    st.write(f"성격: {st.session_state.user_info['personality']}")