import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="미니 냥코대전쟁", layout="centered")
st.title("🐱 미니 냥코대전쟁")

# HTML/JS 기반 게임 코드 (캐릭터 소환 및 이동 추가)
game_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            background-color: #f0f0f0;
            font-family: sans-serif;
        }
        canvas {
            border: 2px solid #333;
            background-color: #e0f7fa;
        }
        .controls {
            margin-top: 10px;
            display: flex;
            gap: 10px;
        }
        button {
            padding: 8px 16px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            border: 2px solid #333;
            border-radius: 6px;
            background-color: #ffffff;
        }
        button:hover {
            background-color: #e0e0e0;
        }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="800" height="300"></canvas>
    
    <div class="controls">
        <button onclick="spawnUnit('basic')">🐱 기본 고양이</button>
        <button onclick="spawnUnit('tank')">🦒 탱커 고양이</button>
    </div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        const groundY = 220;

        // 성 설정
        const playerCastle = { x: 50, y: groundY - 80, width: 60, height: 80, hp: 1000 };
        const enemyCastle = { x: 690, y: groundY - 80, width: 60, height: 80, hp: 1000 };

        // 유닛 목록
        const units = [];

        // 유닛 소환 함수
        function spawnUnit(type) {
            if (type === 'basic') {
                units.push({
                    x: playerCastle.x + playerCastle.width,
                    y: groundY - 25,
                    width: 25,
                    height: 25,
                    speed: 1.2,
                    color: '#ffffff',
                    stroke: '#000000',
                    name: '기본'
                });
            } else if (type === 'tank') {
                units.push({
                    x: playerCastle.x + playerCastle.width,
                    y: groundY - 50,
                    width: 20,
                    height: 50,
                    speed: 0.6,
                    color: '#ffffff',
                    stroke: '#000000',
                    name: '탱커'
                });
            }
        }

        function update() {
            // 유닛 이동 로직
            units.forEach(unit => {
                // 적 성에 도달하기 전까지 이동
                if (unit.x + unit.width < enemyCastle.x) {
                    unit.x += unit.speed;
                }
            });
        }

        function render() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 1. 바닥
            ctx.fillStyle = "#81c784";
            ctx.fillRect(0, groundY, canvas.width, canvas.height - groundY);
            
            ctx.strokeStyle = "#388e3c";
            ctx.lineWidth = 4;
            ctx.beginPath();
            ctx.moveTo(0, groundY);
            ctx.lineTo(canvas.width, groundY);
            ctx.stroke();

            // 2. 아군 성
            ctx.fillStyle = "#42a5f5";
            ctx.fillRect(playerCastle.x, playerCastle.y, playerCastle.width, playerCastle.height);
            ctx.fillStyle = "#1e88e5";
            ctx.beginPath();
            ctx.moveTo(playerCastle.x - 10, playerCastle.y);
            ctx.lineTo(playerCastle.x + playerCastle.width / 2, playerCastle.y - 30);
            ctx.lineTo(playerCastle.x + playerCastle.width + 10, playerCastle.y);
            ctx.closePath();
            ctx.fill();

            // 3. 적군 성
            ctx.fillStyle = "#ef5350";
            ctx.fillRect(enemyCastle.x, enemyCastle.y, enemyCastle.width, enemyCastle.height);
            ctx.fillStyle = "#e53935";
            ctx.beginPath();
            ctx.moveTo(enemyCastle.x - 10, enemyCastle.y);
            ctx.lineTo(enemyCastle.x + enemyCastle.width / 2, enemyCastle.y - 30);
            ctx.lineTo(enemyCastle.x + enemyCastle.width + 10, enemyCastle.y);
            ctx.closePath();
            ctx.fill();

            // 성 이름
            ctx.fillStyle = "#000000";
            ctx.font = "bold 14px sans-serif";
            ctx.textAlign = "center";
            ctx.fillText("아군 성", playerCastle.x + playerCastle.width / 2, playerCastle.y - 40);
            ctx.fillText("적군 성", enemyCastle.x + enemyCastle.width / 2, enemyCastle.y - 40);

            // 4. 유닛 그리기
            units.forEach(unit => {
                // 몸통 (흰색 상자)
                ctx.fillStyle = unit.color;
                ctx.fillRect(unit.x, unit.y, unit.width, unit.height);
                ctx.strokeStyle = unit.stroke;
                ctx.lineWidth = 2;
                ctx.strokeRect(unit.x, unit.y, unit.width, unit.height);

                // 단순한 귀 연출 (삼각형 2개)
                ctx.fillStyle = "#ffffff";
                ctx.beginPath();
                ctx.moveTo(unit.x, unit.y);
                ctx.lineTo(unit.x + 5, unit.y - 6);
                ctx.lineTo(unit.x + 10, unit.y);
                ctx.fill();
                ctx.stroke();

                ctx.beginPath();
                ctx.moveTo(unit.x + unit.width - 10, unit.y);
                ctx.lineTo(unit.x + unit.width - 5, unit.y - 6);
                ctx.lineTo(unit.x + unit.width, unit.y);
                ctx.fill();
                ctx.stroke();
            });
        }

        // 게임 루프 실행 (초당 60프레임)
        function gameLoop() {
            update();
            render();
            requestAnimationFrame(gameLoop);
        }

        gameLoop();
    </script>
</body>
</html>
"""

components.html(game_code, height=380)
