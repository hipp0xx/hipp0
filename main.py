import streamlit as st

# 🌟 페이지 기본 설정 (타이틀, 아이콘, 레이아웃)
st.set_page_config(
    page_title="✨ MBTI 직업 추천 서비스 🚀",
    page_icon="🔮",
    layout="centered"
)

# 🎨 커스텀 스타일링 (배경 및 폰트 감성 추가)
st.markdown("""
    <style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #FF4B4B;
        margin-bottom: 10px;
    }
    .sub-title {
        font-size: 1.1rem;
        text-align: center;
        color: #555555;
        margin-bottom: 30px;
    }
    .card-box {
        background-color: #F0F2F6;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# 🚀 상단 헤더 영역
st.markdown('<div class="main-title">🔮 MBTI 맞춤 직업 탐색기 🎯</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">당신의 성격 유형에 딱 맞는 커리어와 환상의 직무를 찾아드립니다! ✨🌈</div>', unsafe_allow_html=True)

st.divider()

# 📚 풍성한 이모지가 포함된 MBTI 데이터베이스
mbti_db = {
    "INTJ": {
        "title": "🧠 용의주도한 전략가 (Architect)",
        "badge": "⚡ 체스판 위의 지배자 ♟️",
        "desc": "전략적 사고에 능하며, 독창적인 아이디어를 체계적으로 구체화하는 데 독보적입니다! 💡🔍",
        "jobs": [
            "💻 소프트웨어 아키텍트 / AI 연구원 🤖",
            "📊 데이터 과학자 & 퀀트 분석가 📈",
            "🏛️ 경영 컨설턴트 & 전략 기획자 💼",
            "🔬 바이오/과학 분야 연구원 🧪"
        ],
        "strengths": ["🧠 깊은 통찰력", "🎯 목표 지향성", "💡 독창적 문제 해결"],
        "chemistry": "💖 찰떡궁합: ENFP 🎈, ENTP ⚡"
    },
    "INTP": {
        "title": "🔬 논리적인 명상가 (Logician)",
        "badge": "🌌 아이디어 호기심 천재 🧪",
        "desc": "지적 호기심이 끝이 없으며, 복잡한 이론과 원리를 탐구하고 분석하는 것을 즐깁니다! 📖🧩",
        "jobs": [
            "💻 백엔드 / 시스템 개발자 🖥️",
            "⚛️ 물리학자 및 연구원 🔭",
            "🎮 게임 메커닉 디자이너 🕹️",
            "🔐 보안 전문가 / 크립토 분석가 🛡️"
        ],
        "strengths": ["🔍 논리적 분석", "🧠 독창적 생각", "📐 객관적 판단"],
        "chemistry": "💖 찰떡궁합: ENTJ 👑, ENFJ 🌟"
    },
    "ENTJ": {
        "title": "👑 대담한 통솔자 (Commander)",
        "badge": "🔥 야망 찬 카리스마 리더 🎯",
        "desc": "명확한 비전과 강력한 리더십으로 목표를 향해 조직을 이끄는 장군 타입입니다! 🚀🏆",
        "jobs": [
            "🏢 전문 경영인 (CEO/COO) 💼",
            "📈 투자 은행가 (IB) / VC 심사역 💰",
            "⚖️ 기업 전문 변호사 ⚖️",
            "🚩 총괄 프로젝트 매니저 (PM) 🧭"
        ],
        "strengths": ["🚀 결단력", "🎯 비전 제시", "🔥 강력한 추진력"],
        "chemistry": "💖 찰떡궁합: INTP 🔬, INFP 🎨"
    },
    "ENTP": {
        "title": "⚡ 뜨거운 변론가 (Debater)",
        "badge": "💡 끊임없는 아이디어 폭발 💥",
        "desc": "새로운 관점에서 문제를 바라보고, 고정관념을 깨부수는 혁신가입니다! 🌪️🚀",
        "jobs": [
            "🚀 스타트업 연쇄 창업가 🦄",
            "📢 크리에이티브 마케팅 디렉터 🎨",
            "🎙️ 방송 기획자 & 시사 평론가 📺",
            "💡 신사업 개발 매니저 (BD) 🚀"
        ],
        "strengths": ["💥 혁신적 사고", "🗣️ 재치 있는 입담", "⚡ 빠른 상황 판단"],
        "chemistry": "💖 찰떡궁합: INTJ 🧠, INFJ 🦉"
    },
    "INFJ": {
        "title": "🦉 조용한 옹호자 (Advocate)",
        "badge": "🔮 마음을 읽는 통찰가 ✨",
        "desc": "깊은 통찰력과 이타심으로 사람들의 마음을 치유하고 가치 있는 일을 추진합니다! 🕊️🌿",
        "jobs": [
            "🌱 전문 심리상담사 & 코치 🛋️",
            "✍️ 인문학 작가 & 칼럼니스트 📝",
            "🤝 HR 조직문화 담당자 💛",
            "🌍 비영리단체(NGO) 이사 🕊️"
        ],
        "strengths": ["🔮 뛰어난 직관", "💛 깊은 공감 능력", "🎯 명확한 신념"],
        "chemistry": "💖 찰떡궁합: ENFP 🎈, ENTP ⚡"
    },
    "INFP": {
        "title": "🎨 열정적인 중재자 (Mediator)",
        "badge": "🌈 감성 폭발 낭만 예술가 🦄",
        "desc": "풍부한 상상력과 따뜻한 마음으로 세상에 자신만의 예술을 표현합니다! 🎨✨",
        "jobs": [
            "🎨 웹툰 작가 & 일러스트레이터 🖌️",
            "📖 웹소설 작가 & 스토리라이터 ✍️",
            "🎬 영상 콘텐츠 크리에이터 📹",
            "🎶 싱어송라이터 / 음악 프로듀서 🎵"
        ],
        "strengths": ["🌈 풍부한 감성", "💡 독창적 창의성", "🕊️ 따뜻한 진정성"],
        "chemistry": "💖 찰떡궁합: ENFJ 🌟, ENTJ 👑"
    },
    "ENFJ": {
        "title": "🌟 정의로운 사회운동가 (Protagonist)",
        "badge": "☀️ 선한 영향력 멘토 📢",
        "desc": "특유의 카리스마와 진정성으로 주변 사람들에게 꿈과 희망을 전파합니다! 🌈🤝",
        "jobs": [
            "🎓 스타 강사 & 교육 전문가 👨‍🏫",
            "📣 PR/홍보 총괄 디렉터 🎙️",
            "🤝 비영리 이니셔티브 리더 🌍",
            "👥 인재 개발 매니저 (HRD) 💗"
        ],
        "strengths": ["☀️ 뛰어난 리더십", "📢 언변과 설득력", "🤝 따뜻한 포용력"],
        "chemistry": "💖 찰떡궁합: INFP 🎨, ISFP 🖌️"
    },
    "ENFP": {
        "title": "🎈 재기발랄한 활동가 (Campaigner)",
        "badge": "🎉 비타민 같은 인간 에너지 ⚡",
        "desc": "지치지 않는 열정과 사람을 모으는 매력으로 언제나 분위기를 밝게 밝힙니다! 🥳✨",
        "jobs": [
            "🎉 펀(Fun) 이벤트/축제 기획자 🎪",
            "✍️ 광고 카피라이터 💡",
            "📺 방송 리포터 / 유튜버 🎥",
            "✈️ 여행 상품 개발자 🗺️"
        ],
        "strengths": ["🎉 폭발적 에너지를 선사", "💡 무궁무진 아이디어", "🤝 넓은 친화력"],
        "chemistry": "💖 찰떡궁합: INTJ 🧠, INFJ 🦉"
    },
    "ISTJ": {
        "title": "📐 청렴결백한 논리주의자 (Logistician)",
        "badge": "🛡️ 신뢰성 100% 원칙주의자 ⚖️",
        "desc": "철두철미한 원칙 준수와 정확한 일 처리로 조직의 든든한 버팀목이 됩니다! 🏛️📌",
        "jobs": [
            "📊 공인회계사(CPA) & 세무사 🧮",
            "🏛️ 공공기관 행정 전문가 📑",
            "💾 데이터베이스 관리자 (DBA) 💻",
            "🔍 품질 관리 엔지니어 (QA) 🎯"
        ],
        "strengths": ["📐 꼼꼼한 성실함", "🛡️ 강한 책임감", "📊 객관적 일 처리"],
        "chemistry": "💖 찰떡궁합: ESFP 🎭, ESTP 🚀"
    },
    "ISFJ": {
        "title": "🛡️ 용감한 수호자 (Defender)",
        "badge": "🕊️ 세심하고 헌신적인 천사 💖",
        "desc": "남을 돕는 데에서 조용한 보람을 느끼며, 묵묵히 자신의 자리를 지키는 수호자입니다! 🌷🩺",
        "jobs": [
            "🩺 전문 간호사 & 의료 보건인 🏥",
            "🎒 초등 교사 & 보육 교사 🏫",
            "📂 세심한 행정 관리자 📝",
            "🛎️ VIP 고객 서비스 매니저 🤝"
        ],
        "strengths": ["💖 이타적인 세심함", "🌱 인내심과 헌신", "📌 깔끔한 정리 정돈"],
        "chemistry": "💖 찰떡궁합: ESFP 🎭, ESTP 🚀"
    },
    "ESTJ": {
        "title": "📊 엄격한 관리자 (Executive)",
        "badge": "🎯 효율 극대화 오거나이저 💼",
        "desc": "현실적이고 실용적인 감각으로 최고 수준의 효율을 끌어내는 관리의 달인입니다! ⏱️📋",
        "jobs": [
            "🏭 체인점 운영 디렉터 🏢",
            "📉 재무 분석가 / 자산 관리사 💸",
            "👮‍♂️ 경찰관 & 군 장교 🚓",
            "🏗️ 건설 현장 총괄 감독 👷"
        ],
        "strengths": ["📊 뛰어난 조직화", "⏱️ 철저한 시간 관리", "🎯 강한 실행력"],
        "chemistry": "💖 찰떡궁합: ISFP 🖌️, INTP 🔬"
    },
    "ESFJ": {
        "title": "🤝 사교적인 외교관 (Consul)",
        "badge": "🌸 핵인싸 조화주의자 🥳",
        "desc": "누구와도 쉽게 친해지며, 분위기를 훈훈하고 조화롭게 만드는 소통의 달인입니다! ☕🍰",
        "jobs": [
            "✈️ 항공 승무원 (Flight Attendant) 🛫",
            "🎤 공식 행사 진행자 / MC 🎙️",
            "🤝 고객 친화형 영업 팀장 🛍️",
            "💌 고객 경험 (CX) 디자이너 💖"
        ],
        "strengths": ["🌸 넘치는 친화력", "🤝 협동 및 조화", "🎁 풍부한 배려심"],
        "chemistry": "💖 찰떡궁합: ISFP 🖌️, ISTP 🛠️"
    },
    "ISTP": {
        "title": "🛠️ 만능 재주꾼 (Virtuoso)",
        "badge": "🔧 장비 빨 대왕 맥가이버 🏍️",
        "desc": "도구와 기계를 자유자재로 다루며, 위기 상황에서 침착하게 문제를 해결합니다! ⚙️⚡",
        "jobs": [
            "🛠️ 기계/제어 엔지니어 ⚙️",
            "✈️ 항공기 조종사 (Pilot) 👨‍✈️",
            "💻 네트워크 / 인프라 엔지니어 🔌",
            "🏎️ 카레이서 & 정비 전문가 🏁"
        ],
        "strengths": ["⚡ 순간 집중력", "🛠️ 뛰어난 손재주", "🧊 위기 시 침착함"],
        "chemistry": "💖 찰떡궁합: ESFJ 🤝, ESTJ 📊"
    },
    "ISFP": {
        "title": "🖌️ 호기심 많은 예술가 (Adventurer)",
        "badge": "🌿 유유자적 감성 디자이너 🎨",
        "desc": "자유로운 환경에서 미적 감각을 발휘하며, 삶의 순간순간을 예술로 만듭니다! 📸🌱",
        "jobs": [
            "🎨 UI/UX 디자이너 📱",
            "📸 감성 사진작가 📷",
            "👗 패션 스타일리스트 🛍️",
            "🌿 조경가 & 플로리스트 💐"
        ],
        "strengths": ["🎨 뛰어난 미적 감각", "🌿 자율성과 유연함", "💖 따뜻한 서포트"],
        "chemistry": "💖 찰떡궁합: ENFJ 🌟, ESFJ 🤝"
    },
    "ESTP": {
        "title": "🚀 모험을 즐기는 사업가 (Entrepreneur)",
        "badge": "🔥 스릴 중독 해결사 🏎️",
        "desc": "말보다는 행동! 직관적이고 빠르게 움직여 현장의 문제를 단번에 해결합니다! ⚡🎯",
        "jobs": [
            "🏢 공인중개사 & 자산 투자가 🏬",
            "💼 현장 중심 영업 전문가 🤝",
            "🚨 응급구조사 (Paramedic) 🚑",
            "⚽ 프로 스포츠 코치 🏆"
        ],
        "strengths": ["⚡ 즉각적 행동력", "🔥 탁월한 순발력", "🚀 당당한 배짱"],
        "chemistry": "💖 찰떡궁합: ISFJ 🛡️, ISTJ 📐"
    },
    "ESFP": {
        "title": "🎭 자유로운 영혼의 연예인 (Entertainer)",
        "badge": "🌟 무대 위의 주인공 🎤",
        "desc": "어디서나 눈부신 존재감! 주변에 즐거움과 에너지를 팍팍 선물해 주는 분위기 메이커! 🥳🎉",
        "jobs": [
            "🎭 뮤지컬 배우 & 연기자 🎬",
            "🗺️ 버라이어티 투어 가이드 🚌",
            "🎤 이벤터 & 쇼호스트 📺",
            "💄 뷰티/패션 아이콘 💄"
        ],
        "strengths": ["🌟 타고난 연예인 끼", "🥳 무한 긍정 에너지를 발산", "💖 뛰어난 공감"],
        "chemistry": "💖 찰떡궁합: ISFJ 🛡️, ISTJ 📐"
    }
}

# 🎯 MBTI 선택 세션
col1, col2 = st.columns([1, 2])

with col1:
    st.image("https://em-content.zobj.net/source/microsoft-teams/337/crystal-ball_1f52e.png", width=120)

with col2:
    selected_mbti = st.selectbox(
        "👇 당신의 MBTI 4자리를 선택하세요!",
        options=list(mbti_db.keys()),
        index=0
    )

st.write("")

# 🎁 선택 결과 렌더링
if selected_mbti:
    data = mbti_db[selected_mbti]
    
    # 상단 요약 카키 Card
    st.success(f"### {data['title']}")
    st.caption(f"✨ **특징 키워드:** {data['badge']}")
    st.write(f"📝 {data['desc']}")
    
    st.divider()
    
    # 💼 추천 직업 카테고리
    st.markdown("### 💼 ✨ **추천 직업 BEST 4**")
    for job in data["jobs"]:
        st.info(f"👉 **{job}**")
        
    st.divider()
    
    # 🌟 추가 정보 (강점 & 궁합)
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("#### 💪 주요 강점")
        for s in data["strengths"]:
            st.write(f"- {s}")
            
    with c2:
        st.markdown("#### 🤝 환상의 궁합")
        st.write(data["chemistry"])

# 🎈 하단 푸터
st.divider()
st.markdown("<p style='text-align: center; color: #888;'>✨ Created with Streamlit & Emojis 💖</p>", unsafe_allow_html=True)
```eof

알록달록한 이모지와 시각적 요소가 대폭 추가된 `app.py` 파일이 생성되었습니다.

### 🌟 주요 변경 사항:
- 각 MBTI별 명칭, 특징, 강점, 직업 목록에 직관적인 이모지를 대량 추가했습니다.
- 궁합 MBTI(💖 찰떡궁합)와 핵심 강점(💪) 섹션을 신설하여 정보의 풍성함을 더했습니다.
- Streamlit 성공/정보 메시지 상자와 열 구분(`st.columns`) 기능을 활용하여 훨씬 다채롭고 직관적인 UI를 구현했습니다.
