import random
import streamlit as st

# 페이지 설정을 위한 기본 스타일 적용
st.set_page_config(page_title="AI 끝말잇기 게임", page_icon="🎮")

st.markdown(
    """
    <style>
    .stApp {
        background-color: #f5f7f9;
    }
    .chat-bubble {
        padding: 10px 15px;
        border-radius: 15px;
        margin-bottom: 10px;
        width: fit-content;
        max-width: 80%;
    }
    .user-bubble {
        background-color: #0084ff;
        color: white;
        margin-left: auto;
    }
    .ai-bubble {
        background-color: #e5e5ea;
        color: black;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 기본 단어 데이터베이스 (확장 가능)
WORD_DB = [
    "사과",
    "과물",
    "물고기",
    "기차",
    "차표",
    "표범",
    "범인",
    "인형",
    "형사",
    "사진",
    "진주",
    "주스",
    "스파이",
    "이발소",
    "소나무",
    "무지개",
    "개구리",
    "리본",
    "본사",
    "사자",
    "자전거",
    "거미",
    "미소",
    "소구",
    "구름",
    "름표",
]

# 세션 상태 초기화
if "history" not in st.session_state:
    st.session_state.history = []  # (주체, 단어)
if "used_words" not in st.session_state:
    st.session_state.used_words = set()


def get_ai_word(last_char, difficulty):
    # 입력된 마지막 글자로 시작하는 사용 가능한 단어 탐색
    candidates = [
        w
        for w in WORD_DB
        if w.startswith(last_char) and w not in st.session_state.used_words
    ]

    if not candidates:
        return None

    if difficulty == "쉬움":
        # 50% 확률로 단어를 찾지 못한 척(패배) 처리
        if random.random() < 0.5:
            return None
        return random.choice(candidates)

    elif difficulty == "보통":
        return random.choice(candidates)

    elif difficulty == "어려움":
        # 글자 수가 가장 긴 단어를 우선 선택하여 압박
        candidates.sort(key=lambda x: len(x), reverse=True)
        return candidates[0]


# UI 구성
st.title("🎮 AI 끝말잇기 대결")

# 사이드바: 난이도 및 리셋
st.sidebar.header("설정")
difficulty = st.sidebar.selectbox("AI 난이도 선택", ["쉬움", "보통", "어려움"])

if st.sidebar.button("게임 리셋"):
    st.session_state.history = []
    st.session_state.used_words = set()
    st.rerun()

# 대화 기록 출력
st.subheader("대화 기록")
chat_container = st.container()
with chat_container:
    for sender, word in st.session_state.history:
        bubble_class = "user-bubble" if sender == "User" else "ai-bubble"
        st.markdown(
            f'<div class="chat-bubble {bubble_class}"><b>{sender}:</b> {word}</div>',
            unsafe_allow_html=True,
        )

# 입력 폼
with st.form(key="word_form", clear_on_submit=True):
    user_input = st.text_input("단어를 입력하세요:").strip()
    submit_button = st.form_submit_button(label="전송")

if submit_button and user_input:
    # 1. 중복 검사
    if user_input in st.session_state.used_words:
        st.error("이미 사용된 단어입니다!")
    # 2. 끝말잇기 규칙 검사
    elif (
        st.session_state.history
        and not user_input.startswith(st.session_state.history[-1][1][-1])
    ):
        last_char = st.session_state.history[-1][1][-1]
        st.error(f"'{last_char}'(으)로 시작하는 단어를 입력하세요!")
    else:
        # 유저 단어 등록
        st.session_state.history.append(("User", user_input))
        st.session_state.used_words.add(user_input)

        # AI 차례
        ai_reply = get_ai_word(user_input[-1], difficulty)

        if ai_reply:
            st.session_state.history.append(("AI", ai_reply))
            st.session_state.used_words.add(ai_reply)
        else:
            st.balloons()
            st.success("AI가 단어를 떠올리지 못했습니다. 당신의 승리입니다! 🎉")

        st.rerun()
