import streamlit as st
import plotly.graph_objects as go

# 1. 게임 상태 초기화
if "player_y" not in st.session_state:
    st.session_state.player_y = 5.0  # 화살표 Y 위치 (중앙)
    st.session_state.player_x = 2.0  # 화살표 X 위치 (고정)
    st.session_state.obstacles = [[8, 2], [12, 7], [16, 4]]  # 장애물 위치 [X, Y]
    st.session_state.score = 0
    st.session_state.game_over = False

st.title("📐 Streamlit Geometry Dash (Wave Mode)")

if st.session_state.game_over:
    st.error(f"💥 게임 오버! 최종 점수: {st.session_state.score}")
    if st.button("다시 시작"):
        st.session_state.player_y = 5.0
        st.session_state.obstacles = [[8, 2], [12, 7], [16, 4]]
        st.session_state.score = 0
        st.session_state.game_over = False
        st.rerun()
else:
    # 2. 이동 조작 함수 (화살표 움직임)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬆️ 상승 (대각선 위로)"):
            st.session_state.player_y = min(10.0, st.session_state.player_y + 1.0)
            st.session_state.score += 1
    with col2:
        if st.button("⬇️ 하강 (대각선 아래로)"):
            st.session_state.player_y = max(0.0, st.session_state.player_y - 1.0)
            st.session_state.score += 1

    # 장애물 이동 처리
    new_obstacles = []
    for obs in st.session_state.obstacles:
        obs_x, obs_y = obs[0] - 1, obs[1]  # 화면 왼쪽으로 이동
        
        # 충돌 판정 (화살표와 장애물 거리 체크)
        if obs_x == st.session_state.player_x and abs(obs_y - st.session_state.player_y) < 1.0:
            st.session_state.game_over = True
            
        # 화면 밖으로 나간 장애물 재배치
        if obs_x < 0:
            obs_x = 15
            import random
            obs_y = random.randint(1, 9)
            
        new_obstacles.append([obs_x, obs_y])
    
    st.session_state.obstacles = new_obstacles

    # 3. 렌더링 (Plotly를 활용한 화면 그리기)
    fig = go.Figure()

    # 플레이어 (화살표/Wave)
    fig.add_trace(go.Scatter(
        x=[st.session_state.player_x], 
        y=[st.session_state.player_y],
        mode='markers',
        marker=dict(size=20, symbol='triangle-right', color='cyan'),
        name='Player'
    ))

    # 장애물
    obs_x = [o[0] for o in st.session_state.obstacles]
    obs_y = [o[1] for o in st.session_state.obstacles]
    fig.add_trace(go.Scatter(
        x=obs_x, 
        y=obs_y,
        mode='markers',
        marker=dict(size=25, symbol='square', color='red'),
        name='Obstacle'
    ))

    # 화면 설정 (맵 범위 고정)
    fig.update_layout(
        xaxis=dict(range=[0, 15], showgrid=False, zeroline=False),
        yaxis=dict(range=[0, 10], showgrid=False, zeroline=False),
        height=400,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor='black'
    )

    st.plotly_chart(fig, use_container_width=True)
    st.write(f"**현재 점수:** {st.session_state.score}")
