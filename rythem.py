import streamlit as st
import random

# 1. 게임 상태 초기화
if "player_y" not in st.session_state:
    st.session_state.player_y = 3  # Player position (Y: 0~6)
    st.session_state.obstacles = [10, 15, 20]  # Obstacle X positions
    st.session_state.obs_y = [2, 5, 1]  # Obstacle Y positions
    st.session_state.score = 0
    st.session_state.game_over = False

st.title("📐 Streamlit Geometry Dash (Wave)")

if st.session_state.game_over:
    st.error(f"💥 게임 오버! 최종 점수: {st.session_state.score}")
    if st.button("다시 시작"):
        st.session_state.player_y = 3
        st.session_state.obstacles = [10, 15, 20]
        st.session_state.obs_y = [2, 5, 1]
        st.session_state.score = 0
        st.session_state.game_over = False
        st.rerun()
else:
    # 2. 이동 조작
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬆️ 상승"):
            st.session_state.player_y = max(0, st.session_state.player_y - 1)
            st.session_state.score += 1
    with col2:
        if st.button("⬇️ 하강"):
            st.session_state.player_y = min(6, st.session_state.player_y + 1)
            st.session_state.score += 1

    # 3. 장애물 이동 및 충돌 처리
    player_x = 2
    for i in range(len(st.session_state.obstacles)):
        st.session_state.obstacles[i] -= 1

        # 충돌 검사
        if st.session_state.obstacles[i] == player_x:
            if st.session_state.obs_y[i] == st.session_state.player_y:
                st.session_state.game_over = True

        # 화면 밖으로 나가면 재배치
        if st.session_state.obstacles[i] < 0:
            st.session_state.obstacles[i] = 12
            st.session_state.obs_y[i] = random.randint(0, 6)

    # 4. 화면 그리기 (텍스트 기반 격자)
    grid_height = 7
    grid_width = 13
    
    board = [["⬛" for _ in range(grid_width)] for _ in range(grid_height)]

    # 장애물 표시
    for ox, oy in zip(st.session_state.obstacles, st.session_state.obs_y):
        if 0 <= ox < grid_width:
            board[oy][ox] = "🟥"

    # 플레이어(화살표) 표시
    board[st.session_state.player_y][player_x] = "🔷"

    # 렌더링
    screen_text = "\n".join(["".join(row) for row in board])
    st.code(screen_text, language=None)
    st.write(f"**현재 점수:** {st.session_state.score}")
