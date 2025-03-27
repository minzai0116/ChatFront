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

# secrets.toml에서 GEMINI_API_KEY 읽어오기
gemini_api_key = st.secrets["general"]["GEMINI_API_KEY"]

# Google Gemini API 설정
genai.configure(api_key=gemini_api_key)

st.title("마음의 소리")

# 세션 상태 초기화 (대화 내용 저장)
if "conversation_sections" not in st.session_state:
    st.session_state.conversation_sections = []  # 대화 내용 저장

if "current_conversation" not in st.session_state:
    st.session_state.current_conversation = []  # 현재 대화 내용 저장

if "selected_style" not in st.session_state:
    st.session_state.selected_style = None  # 스타일 초기화

# 상담 스타일을 세션 상태에 저장하고 페이지 리로딩
def update_style(counseling_style):
    st.session_state.selected_style = counseling_style
    st.session_state.show_style_selector = False  # 스타일 선택 UI 숨기기
    st.rerun()  # 페이지 리로딩

# 사이드바에서 상담 스타일 선택
st.sidebar.title("Select Counseling Style")
counseling_style = st.sidebar.radio(
    "Choose a style for the conversation:",
    ["친구같이 다정한 스타일", "이야기를 들어주며 공감과 위로를 해주는 스타일", "상황에 알맞는 현실적인 조언을 해주는 스타일"],
    index=["친구같이 다정한 스타일", "이야기를 들어주며 공감과 위로를 해주는 스타일", "상황에 알맞는 현실적인 조언을 해주는 스타일"].index(st.session_state.selected_style) if st.session_state.selected_style else 0
)

if counseling_style != st.session_state.selected_style:
    update_style(counseling_style)

# 상담 스타일에 맞는 프롬프트 설정
def get_personality_prompt(style):
    if style == "친구같이 다정한 스타일":
        return "당신은 친근하고 다정한 친구처럼 대답해주세요."
    elif style == "이야기를 들어주며 공감과 위로를 해주는 스타일":
        return "당신은 상대방의 이야기를 잘 듣고, 공감하며 위로하는 스타일로 대답해주세요."
    elif style == "상황에 알맞는 현실적인 조언을 해주는 스타일":
        return "당신은 상황에 맞는 현실적이고 실용적인 조언을 해주세요."
    else:
        return "일반적인 대화를 원합니다."

# 상담 스타일에 맞는 프롬프트 가져오기
personality_prompt = get_personality_prompt(st.session_state.selected_style)
st.session_state.personality_prompt = personality_prompt  # 성격 정보 세션 상태에 저장

# Save & New Conversation 버튼
if st.sidebar.button("Save & New Conversation"):
    if st.session_state.current_conversation:
        st.session_state.conversation_sections.append(st.session_state.current_conversation)  # 현재 대화 저장
    st.session_state.current_conversation = []  # 새로운 대화 시작
    st.session_state.selected_style = None  # 스타일 초기화
    st.rerun()  # 페이지 리로딩

# 상담 스타일을 채팅 화면 상단에 표시
if st.session_state.selected_style:
    st.markdown(f"**상담 스타일: {st.session_state.selected_style}**")  # 채팅 화면 상단에 스타일 표시

# 대화 섹션을 사이드바에서 표시
st.sidebar.title("Previous Conversations")

# 저장된 대화 섹션을 사이드바에서 보여주기
for idx, conversation in enumerate(st.session_state.conversation_sections):
    col1, col2 = st.columns([4, 1])

    with col1:
        # 대화 목록 표시
        if st.sidebar.button(f"Conversation {idx + 1}", key=idx):
            st.session_state.current_conversation = conversation

    with col2:
        # 삭제 버튼을 "❌"로 표시
        if st.sidebar.button(f"❌", key=f"delete_{idx}"):
            del st.session_state.conversation_sections[idx]
            st.session_state.current_conversation = []
            st.rerun()  # 페이지 리로딩

# 현재 대화 표시
if "current_conversation" in st.session_state and st.session_state.current_conversation:
    for message in st.session_state.current_conversation:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 사용자 입력 받기
if prompt := st.chat_input("오늘 당신의 마음의 소리는 무엇인가요?"):
    st.session_state.current_conversation.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # 성격에 맞는 프롬프트와 사용자 메시지 결합
            full_prompt = f"{st.session_state.personality_prompt} 사용자 메시지: {prompt}"

            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(full_prompt)

            st.markdown(response.text)

            st.session_state.current_conversation.append({"role": "assistant", "content": response.text})

        except Exception as e:
            st.error(f"Error generating response: {e}")


# 대화 내용 저장
def save_conversation():
    conversation_text = "\n".join([f"{message['role']}: {message['content']}" for message in st.session_state.current_conversation])

    # 대화 내용을 바로 다운로드
    st.sidebar.download_button(
        label="TXT파일로 저장하기",
        data=conversation_text,
        file_name="conversation.txt",
        mime="text/plain"
    )
    
    # 대화 저장 완료 메시지 표시
    st.sidebar.success("Conversation saved and ready to download!")

# Save Conversation 버튼 클릭 시
if st.sidebar.button("대화 파일로 만들기"):
    save_conversation()
