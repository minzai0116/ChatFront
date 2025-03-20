import streamlit as st
import google.generativeai as genai

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

# `secrets.toml`에서 GEMINI_API_KEY 읽어오기
gemini_api_key = st.secrets["general"]["GEMINI_API_KEY"]

# Google Gemini API 설정
genai.configure(api_key=gemini_api_key)

st.title("Cap Chatbot")

# 세션 상태 초기화 (대화 내용 저장)
if "conversation_sections" not in st.session_state:
    st.session_state.conversation_sections = []  # 대화 내용 저장

if "current_conversation" not in st.session_state:
    st.session_state.current_conversation = []  # 현재 대화 내용 저장

# Recent Conversation 버튼 - 현재 대화를 저장
if st.sidebar.button("Save Conversation"):
    if st.session_state.current_conversation:
        st.session_state.conversation_sections.append(st.session_state.current_conversation)
    st.sidebar.success("Conversation saved!")  # 알림 메시지 표시

# 새로 대화 시작하기 버튼
if st.sidebar.button("Start New Conversation"):
    # 새로운 대화 시작
    st.session_state.current_conversation = []  # 새로운 대화 시작
    st.rerun()  # 페이지 리로딩

# 대화 섹션을 사이드바에서 표시
st.sidebar.title("Previous Conversations")

# 저장된 대화 섹션을 사이드바에서 보여주기
for idx, conversation in enumerate(st.session_state.conversation_sections):
    
    # 대화 목록과 삭제 버튼을 나란히 배치
    col1, col2 = st.columns([4, 1])

    with col1:
        # 대화 목록 표시
        if st.sidebar.button(f"Conversation {idx + 1}", key=idx):
            # 선택된 대화 섹션을 화면에 표시
            st.session_state.current_conversation = conversation

    with col2:
        # 삭제 버튼을 "❌"로 표시 (삭제 버튼을 대화 옆에 배치)
        if st.sidebar.button(f"❌", key=f"delete_{idx}"):
            # 해당 대화 삭제
            del st.session_state.conversation_sections[idx]
            st.session_state.current_conversation = []  # 현재 대화 초기화
            st.rerun()  # 페이지 리로딩

# 현재 대화 표시 (현재 대화가 있으면 보여줌)
if "current_conversation" in st.session_state and st.session_state.current_conversation:
    # 현재 대화 메시지 표시
    for message in st.session_state.current_conversation:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 선택된 대화 표시
if "selected_conversation" in st.session_state:
    # 선택된 대화만 표시
    for message in st.session_state.selected_conversation:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
# 성격에 맞는 프롬프트 생성 함수
def get_personality_prompt(personality):
    if personality == "외향적":
        return "당신은 사교적이고 외향적인 성격을 가졌습니다. 긍정적이고 에너지 넘치는 답변을 주세요."
    elif personality == "내향적":
        return "당신은 내성적이고 차분한 성격을 가졌습니다. 차분하고 신중한 답변을 주세요."
    elif personality == "분석적":
        return "당신은 논리적이고 분석적인 성격을 가졌습니다. 분석적이고 논리적인 답변을 주세요."
    elif personality == "감성적":
        return "당신은 감성적이고 감정이 풍부한 성격을 가졌습니다. 감성적이고 따뜻한 답변을 주세요."
    else:
        return "일반적인 대화를 원합니다."

# Chatbot 페이지에서 성격 정보 불러오기
if "user_info" in st.session_state:
    user_personality = st.session_state.user_info.get("personality", None)
else:
    user_personality = None

# 사이드바에서 성격 정보 출력
if user_personality:
    st.sidebar.markdown(f"**당신의 성격은: {user_personality}**")  # 성격 정보 사이드바에 출력
else:
    st.sidebar.markdown("**No personality information found.**")  # 성격 정보가 없을 경우 메시지 출력

# 성격에 맞는 프롬프트 생성
personality_prompt = get_personality_prompt(user_personality) if user_personality else "일반적인 대화를 원합니다."

# 사용자 입력 받기
prompt = st.text_input("오늘 하루는 어떠셨나요?")  # st.chat_input 대신 사용
if prompt := st.chat_input("What is up?"):
    # 사용자가 입력한 메시지 저장
    st.session_state.current_conversation.append({"role": "user", "content": prompt})

    # 사용자 메시지 표시
    with st.chat_message("user"):
        st.markdown(prompt)

    # Google Gemini API 호출 (모델 수정: "gemini-2.0-flash")
    with st.chat_message("assistant"):
        try:
            # "gemini-2.0-flash" 모델을 사용하여 응답 생성
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(prompt)

            # 챗봇 응답 표시
            st.markdown(response.text)
            
            # 응답을 현재 대화 섹션에 저장
            st.session_state.current_conversation.append({"role": "assistant", "content": response.text})

        except Exception as e:
            st.error(f"Error generating response: {e}")
