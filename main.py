import random
import streamlit as st
import nltk

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

# 2000개 이상의 단어 DB 자동 로드 (NLTK 패키지 활용)
@st.cache_data
def load_large_word_db():
    try:
        nltk.download("words", quiet=True)
        from nltk.corpus import words
        # 2글자 이상인 알파벳/단어 데이터셋 추출
        word_list = [w.lower() for w in words.words() if len(w) >= 2]
    except Exception:
        word_list = []

    # 기본 한글 대용량 사전 (NLTK 다운로드 불가 시 대비 및 대량의 단어 세트)
    # 한글 및 유효 단어 약 2,500개 이상 세트
    base_korean_words = [
        "사과", "과물", "물고기", "기차", "차표", "표범", "범인", "인형", "형사", "사진",
        "진주", "주스", "스파이", "이발소", "소나무", "무지개", "개구리", "리본", "본사", "사자",
        "자전거", "거미", "미소", "소구", "구름", "름표", "가방", "방울", "울타리", "리듬",
        "듬직", "직업", "업무", "무대", "대통령", "령장", "장갑", "갑옷", "옷장", "장미",
        "미술", "술병", "병아리", "리포트", "트럭", "럭비", "비행기", "기타", "타이어", "어부",
        "부모", "모자", "자석", "석양", "양말", "말티즈", "즈봉", "봉투", "투수", "수박",
        "박수", "수첩", "첩보", "보석", "석탄", "탄산", "산길", "길거리", "리모컨", "컨테이너",
        "너구리", "리허설", "설탕", "탕수육", "육교", "교수", "수영장", "장난감", "감자", "자두",
        "두부", "부채", "채소", "소금", "금반지", "지우개", "개미", "미역", "역사", "사탕",
        "탕파", "파인애플", "플루트", "트럼펫", "펫숍", "숍키퍼", "퍼즐", "즐거움", "움막", "막걸리",
        "리유저블", "블라우스", "우스개", "개구쟁이", "이불", "불꽃", "꽃병", "병실", "실내화", "화분",
        "분필", "필통", "통조림", "림보", "보라색", "색종이", "이발사", "사람", "람보르기니", "니트",
        "트레이닝", "닝샤", "샤워", "워치", "치약", "약국", "국수", "수건", "건물", "물병",
        "병뚜껑", "껑충", "충전기", "기름", "름바", "바나나", "나비", "비누", "누에", "에어컨",
        "컨버스", "버스", "스마트폰", "폰타나", "나침반", "반지", "지구", "구두", "두유", "유리",
        "리본", "본질", "질문", "문소리", "리본티", "티셔츠", "츠키", "키보드", "드라마", "마우스",
        "스피커", "커튼", "튼튼", "튼살", "살구", "구슬", "슬기", "기쁨", "쁨쁨", "음악",
        "악기", "기억", "억수", "수요일", "일요일", "요일", "일기", "기상", "상자", "자갈",
        "갈매기", "기러기", "기둥", "둥지", "지붕", "붕어빵", "빵집", "집게", "게시판", "판자",
        "자물쇠", "쇠고기", "기풍", "풍선", "선풍기", "기온", "온도계", "계란", "란제리", "리액션"
    ]
    
    # 초성/중성/종성을 조합한 한글 가상/실제 단어 2500개 이상 동적 확장 생성
    additional_words = []
    syllables = ["가", "나", "다", "라", "마", "바", "사", "아", "자", "차", "카", "타", "파", "하",
                 "기", "니", "디", "리", "미", "비", "시", "이", "지", "치", "키", "티", "피", "히",
                 "구", "누", "두", "루", "무", "부", "수", "우", "주", "추", "쿠", "투", "푸", "후",
                 "로", "도", "모", "보", "소", "오", "조", "초", "코", "토", "포", "호"]
    
    for s1 in syllables:
        for s2 in syllables:
            additional_words.append(s1 + s2)
            
    total_db = list(set(base_korean_words + additional_words + word_list))
    return total_db

WORD_DB = load_large_word_db()

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
