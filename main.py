import random
import streamlit as st

st.set_page_config(page_title="무한의 계단", page_icon="🪜")

# 게임 상태 초기화
if "score" not in st.session_state:
    st.session_state.score = 0
if "character_pos" not in st.session_state:
    st.session_state.character_pos = 0  # 0: 왼쪽, 1: 오른쪽
if "stairs" not in st.session_state:
    st.session_state.stairs = [random.choice([0, 1]) for _ in range(20)]
if "game_over" not in st.session_state:
    st.session_state.game_over = False


def reset_game():
    st.session_state.score = 0
    st.session_state.character_pos = 0
    st.session_state.stairs = [random.choice([0, 1]) for _ in range(20)]
    st.session_state.game_over = False


def move(action):
    if st.session_state.game_over:
        return

    if action == "turn":
        st.session_state.character_pos = 1 - st.session_state.character_pos

    next_stair = st.session_state.stairs[0]

    if st.session_state.character_pos == next_stair:
        st.session_state.score += 1
        st.session_state.stairs.pop(0)
        st.session_state.stairs.append(random.choice([0, 1]))
    else:
        st.session_state.game_over = True


# UI 구성을 위한 화면 처리
st.title("🪜 무한의 계단")
st.subheader(f"현재 점수: {st.session_state.score}")

if st.session_state.game_over:
    st.error(f"게임 오버! 최종 점수: {st.session_state.score}")
    st.button("다시 시작", on_click=reset_game)
else:
    st.write("---")
    st.write(
        f"캐릭터 방향: **{'왼쪽' if st.session_state.character_pos == 0 else '오른쪽'}**"
    )

    stair_display = ""
    for s in st.session_state.stairs[:7][::-1]:
        stair_display += "🟩 " if s == 1 else "🟦 "
        stair_display += "\n\n"
    st.text(f"다가오는 계단:\n{stair_display}")

    st.write("---")

    col1, col2 = st.columns(2)
    with col1:
        st.button("⬆️ 오르기", on_click=move, args=("climb",), use_container_width=True)
    with col2:
        st.button("↩️ 방향틀기", on_click=move, args=("turn",), use_container_width=True)
