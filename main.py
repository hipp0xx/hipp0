import random
import time
import streamlit as st

st.set_page_config(page_title="무한의 계단 (그래픽 Ver.)", page_icon="🪜")

# --- 1. 게임 상태 초기화 및 관리 ---
if "score" not in st.session_state:
    st.session_state.score = 0
if "character_pos" not in st.session_state:
    st.session_state.character_pos = 0  # 0: 왼쪽, 1: 오른쪽
if "stairs" not in st.session_state:
    # 초기 계단 랜덤 생성 (0: 왼쪽, 1: 오른쪽)
    st.session_state.stairs = [random.choice([0, 1]) for _ in range(25)]
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "climb_animation" not in st.session_state:
    st.session_state.climb_animation = False


def reset_game():
    st.session_state.score = 0
    st.session_state.character_pos = 0
    st.session_state.stairs = [random.choice([0, 1]) for _ in range(25)]
    st.session_state.game_over = False
    st.session_state.climb_animation = False


def process_move(action):
    """
    action: 'climb' (오르기) 또는 'turn' (방향틀기)
    """
    if st.session_state.game_over:
        return

    # 방향틀기 처리
    if action == "turn":
        st.session_state.character_pos = 1 - st.session_state.character_pos

    # 현재 발밑 계단의 방향 확인
    current_stair_dir = st.session_state.stairs[0]

    # 캐릭터 방향과 계단 방향이 일치하는지 검사
    if st.session_state.character_pos == current_stair_dir:
        # 성공: 점수 증가 및 새 계단 생성
        st.session_state.score += 1
        st.session_state.stairs.pop(0)  # 맨 아래 계단 제거
        st.session_state.stairs.append(random.choice([0, 1]))  # 맨 위에 새 계단 추가
        
        # 오르기 모션 효과를 위한 상태 (잠시 '올라가는 중' 이모지 표시)
        if action == "climb":
            st.session_state.climb_animation = True
    else:
        # 실패: 게임 오버
        st.session_state.game_over = True
        st.session_state.climb_animation = False


# --- 2. UI
