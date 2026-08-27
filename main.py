import random
import streamlit as st

st.set_page_config(page_title="AI 끝말잇기 게임", page_icon="🎮")

# 심플한 UI 스타일링
st.markdown(
    """
    <style>
    .stApp { background-color: #f8f9fa; }
    .chat-bubble {
        padding: 10px 15px;
        border-radius: 15px;
        margin-bottom: 8px;
        max-width: 70%;
        font-size: 16px;
    }
    .user-bubble {
        background-color: #007bff;
        color: white;
        margin-left: auto;
        text-align: right;
    }
    .ai-bubble {
        background-color: #e9ecef;
        color: #212529;
        margin-right: auto;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 단어 데이터베이스
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
    st.session_state.history = []  # [(발화자, 단어), ...]
if "used_words" not in st.session_state:
    st.session_state.used_words = set()
if "game_over" not in st.session_state:
    st.session_state.game_over = False


def get_ai_word(last_char, difficulty):
    """AI가 난이도에 따라 단 한 개의 단어만 선택해 반환"""
    candidates = [
        w
        for w in WORD_DB
        if w.startswith(last_char) and w not in st.session_state.used_words
    ]

    if not candidates:
        return None

    if difficulty == "쉬움":
        # 40% 확률로 기권
        if random.random() < 0.4:
            return None
        return random.choice(candidates)
    elif difficulty == "보통":
        return random.choice(candidates)
    elif difficulty == "어려움":
        # 긴 단어 우선 선택
        candidates.sort(key=lambda x: len(x), reverse=True)
        return candidates[0]


st.title("🎮 AI 끝말잇기 대결")

# 사이드바 설정
st.sidebar.header("설정")
difficulty = st.sidebar.selectbox("AI 난이도 선택", ["쉬움", "보통", "어려움"])

if st.sidebar.button("게임 다시 시작"):
    st.session_state.history = []
    st.session_state.used_words = set()
    st.session_state.game_over = False
    st.rerun()

# 기존 대화 기록 출력
for sender, word in st.session_state.history:
    bubble_class = "user-bubble" if sender == "User" else "ai-bubble"
    st.markdown(
        f'<div class="chat-bubble {bubble_class}"><b>{sender}:</b> {word}</div>',
        unsafe_allow_html=True,
    )

# 게임 진행 로직
if not st.session_state.game_over:
    with st.form(key="word_form", clear_on_submit=True):
        user_input = st.text_input("단어를 입력하세요:").strip()
        submit_button = st.form_submit_button(label="전송")

    if submit_button and user_input:
        # 1. 중복 검증
        if user_input in st.session_state.used_words:
            st.warning("이미 사용된 단어입니다!")

        # 2. 첫 글자 규칙 검증
        elif (
            st.session_state.history
            and not user_input.startswith(st.session_state.history[-1][1][-1])
        ):
            needed_char = st.session_state.history[-1][1][-1]
            st.warning(f"'{needed_char}'(으)로 시작하는 단어를 입력하세요!")

        else:
            # [유저 차례] 단어 1개 추가
            st.session_state.history.append(("User", user_input))
            st.session_state.used_words.add(user_input)

            # [AI 차례] 단어 1개 답장 생성
            ai_reply = get_ai_word(user_input[-1], difficulty)

            if ai_reply:
                st.session_state.history.append(("AI", ai_reply))
                st.session_state.used_words.add(ai_reply)
            else:
                st.balloons()
                st.success(
                    "AI가 이어갈 단어를 찾지 못했습니다! 당신의 승리입니다! 🎉"
                )
                st.session_state.game_over = True

            st.rerun()
else:
    st.info("게임이 종료되었습니다. 사이드바의 [게임 다시 시작] 버튼을 눌러주세요.")
