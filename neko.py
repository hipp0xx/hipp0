import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="미니 냥코대전쟁", layout="centered")
st.title("🐱 미니 냥코대전쟁")

# HTML/JS 기반 게임 화면 구성
game_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            background-color: #f0f0f0;
        }
        canvas {
            border: 2px solid #333;
            background-color: #e0f7fa; /* 하늘색 배경 */
        }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="800" height="300"></canvas>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        const groundY = 220;

        // 성 기본 정보
        const playerCastle = { x: 50, y: groundY - 80, width: 60, height: 80, hp: 1000 };
        const enemyCastle = { x: 690, y: groundY - 80, width: 60, height: 80, hp: 1000 };

        function render() {
            // 캔버스 초기화
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 1. 바닥 (초록색 땅)
            ctx.fillStyle = "#81c784";
            ctx.fillRect(0, groundY, canvas.width, canvas.height - groundY);
            
            ctx.strokeStyle = "#388e3c";
            ctx.lineWidth = 4;
            ctx.beginPath();
            ctx.moveTo(0, groundY);
            ctx.lineTo(canvas.width, groundY);
            ctx.stroke();

            // 2. 아군 성 (파란색 단순 도형)
            ctx.fillStyle = "#42a5f5";
            ctx.fillRect(playerCastle.x, playerCastle.y, playerCastle.width, playerCastle.height);
            
            // 아군 성 지붕
            ctx.fillStyle = "#1e88e5";
            ctx.beginPath();
            ctx.moveTo(playerCastle.x - 10, playerCastle.y);
            ctx.lineTo(playerCastle.x + playerCastle.width / 2, playerCastle.y - 30);
            ctx.lineTo(playerCastle.x + playerCastle.width + 10, playerCastle.y);
            ctx.closePath();
            ctx.fill();

            // 3. 적군 성 (빨간색 단순 도형)
            ctx.fillStyle = "#ef5350";
            ctx.fillRect(enemyCastle.x, enemyCastle.y, enemyCastle.width, enemyCastle.height);

            // 적군 성 지붕
            ctx.fillStyle = "#e53935";
            ctx.beginPath();
            ctx.moveTo(enemyCastle.x - 10, enemyCastle.y);
            ctx.lineTo(enemyCastle.x + enemyCastle.width / 2, enemyCastle.y - 30);
            ctx.lineTo(enemyCastle.x + enemyCastle.width + 10, enemyCastle.y);
            ctx.closePath();
            ctx.fill();

            // 4. 성 이름 텍스트
            ctx.fillStyle = "#000000";
            ctx.font = "bold 14px sans-serif";
            ctx.textAlign = "center";
            ctx.fillText("아군 성", playerCastle.x + playerCastle.width / 2, playerCastle.y - 40);
            ctx.fillText("적군 성", enemyCastle.x + enemyCastle.width / 2, enemyCastle.y - 40);
        }

        render();
    </script>
</body>
</html>
"""

# Streamlit 화면에 렌더링
components.html(game_code, height=320)
