import random
import streamlit as st
from streamlit_keyboard_jsx import keyboard

st.set_page_config(page_title="무한의 계단", page_icon="🪜", layout="centered")

# --- 게임 상태 초기화 ---
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "score" not in st.session_state:
    st.session_state.score = 0
if "character_dir" not in st.session_state:
    st.session_state.character_dir = 1  # 1: 오른쪽, -1: 왼쪽
if "stairs" not in st.session_state:
    # 계단 방향 생성 (1: 오른쪽 위, -1: 왼쪽 위)
    st.session_state.stairs = [1]
    for _ in range(15):
        st.session_state.stairs.append(random.choice([1, -1]))

# --- 게임 로직 함수 ---
def climb():
    """오르기: 현재 바라보는 방향 그대로 한 단 올라감"""
    if st.session_state.game_over:
        return
    
    target_dir = st.session_state.stairs[0]
    if st.session_state.character_dir == target_dir:
        # 성공: 계단 소모 및 새로운 계단 추가
        st.session_state.score += 1
        st.session_state.stairs.pop(0)
        st.session_state.stairs.append(random.choice([1, -1]))
    else:
        # 실패: 방향이 맞지 않음
        st.session_state.game_over = True

def turn_and_climb():
    """방향 전환: 바라보는 방향을 바꾼 후 한 단 올라감"""
    if st.session_state.game_over:
        return
    
    st.session_state.character_dir *= -1
    climb()

def reset_game():
    st.session_state.game_over = False
    st.session_state.score = 0
    st.session_state.character_dir = 1
    st.session_state.stairs = [1]
    for _ in range(15):
        st.session_state.stairs.append(random.choice([1, -1]))

# --- UI 레이아웃 ---
st.title("🪜 무한의 계단 (Streamlit Ver.)")
st.caption("키보드 [방향키 왼쪽/오른쪽] 또는 화면 버튼을 사용해 계단을 올라가세요!")

# 점수 표시
st.metric(label="현재 점수", value=f"{st.session_state.score} 계단")

# 게임 화면 시각화 (텍스트 기반)
st.subheader("--- 게임 화면 ---")

display_lines = []
for i, s_dir in enumerate(st.session_state.stairs[:8]):
    dir_str = "👉 (오른쪽)" if s_dir == 1 else "👈 (왼쪽)"
    if i == 0:
        char_str = "🏃 (캐릭터)" if st.session_state.character_dir == 1 else "(캐릭터) 🏃"
        display_lines.append(f"**[현재 위치]** 계단 방향: {dir_str} | {char_str}")
    else:
        display_lines.append(f"계단 {i+1}: {dir_str}")

for line in display_lines:
    st.write(line)

st.write("---")

# --- 조작부 ---
if not st.session_state.game_over:
    col1, col2 = st.columns(2)
    
    # 방향에 따라 버튼 역할 매핑
    with col1:
        st.button("⬅️ 방향 전환 후 오르기", on_click=turn_and_climb, use_container_width=True)
    with col2:
        st.button("⬆️ 그대로 오르기", on_click=climb, use_container_width=True)

    # 키보드 이벤트 감지 (왼쪽/오른쪽 화살표)
    key_event = keyboard(key_cause_event_down=["ArrowLeft", "ArrowRight"])
    if key_event == "ArrowLeft":
        if st.session_state.character_dir == -1:
            climb()
        else:
            turn_and_climb()
        st.rerun()
    elif key_event == "ArrowRight":
        if st.session_state.character_dir == 1:
            climb()
        else:
            turn_and_climb()
        st.rerun()

else:
    st.error(f"💥 게임 오버! 최종 기록: {st.session_state.score} 계단")
    st.button("🔄 다시 시작하기", on_click=reset_game, use_container_width=True)
