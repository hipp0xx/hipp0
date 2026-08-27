import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Streamlit Pac-Man", layout="centered")

st.title("🟡 Streamlit 팩맨 게임")
st.write("방향키(⬆️ ⬇️ ⬅️ ➡️)를 사용해 쿠키를 모두 먹으세요!")

# HTML/JS 기반 팩맨 게임 코드
pacman_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            background-color: #111;
            color: white;
            text-align: center;
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 10px;
        }
        canvas {
            border: 4px solid blue;
            background-color: black;
            box-shadow: 0 0 15px rgba(0, 0, 255, 0.5);
        }
        #score {
            font-size: 20px;
            margin-bottom: 10px;
            color: #yellow;
        }
    </style>
</head>
<body>
    <div id="score">SCORE: <span id="scoreVal">0</span></div>
    <canvas id="canvas" width="400" height="400"></canvas>

    <script>
        const canvas = document.getElementById("canvas");
        const ctx = canvas.getContext("2d");
        const scoreElem = document.getElementById("scoreVal");

        const tileSize = 40;
        let score = 0;

        // 1: 벽, 2: 쿠키, 0: 빈 공간
        const map = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 2, 2, 2, 1, 2, 2, 2, 2, 1],
            [1, 2, 1, 2, 1, 2, 1, 1, 2, 1],
            [1, 2, 1, 2, 2, 2, 2, 1, 2, 1],
            [1, 2, 1, 1, 1, 1, 2, 1, 2, 1],
            [1, 2, 2, 2, 0, 2, 2, 1, 2, 1],
            [1, 1, 1, 2, 1, 1, 2, 1, 2, 1],
            [1, 2, 2, 2, 2, 1, 2, 2, 2, 1],
            [1, 2, 1, 1, 2, 2, 2, 1, 2, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ];

        let pacman = { x: 1, y: 1, dx: 0, dy: 0, mouth: 0.2 };

        document.addEventListener("keydown", (e) => {
            if (e.key === "ArrowUp") { pacman.dx = 0; pacman.dy = -1; }
            else if (e.key === "ArrowDown") { pacman.dx = 0; pacman.dy = 1; }
            else if (e.key === "ArrowLeft") { pacman.dx = -1; pacman.dy = 0; }
            else if (e.key === "ArrowRight") { pacman.dx = 1; pacman.dy = 0; }
        });

        function update() {
            let nextX = pacman.x + pacman.dx;
            let nextY = pacman.y + pacman.dy;

            if (map[nextY] && map[nextY][nextX] !== 1) {
                pacman.x = nextX;
                pacman.y = nextY;

                if (map[pacman.y][pacman.x] === 2) {
                    map[pacman.y][pacman.x] = 0;
                    score += 10;
                    scoreElem.innerText = score;
                }
            }
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 맵 그리기
            for (let r = 0; r < map.length; r++) {
                for (let c = 0; c < map[r].length; c++) {
                    if (map[r][c] === 1) {
                        ctx.fillStyle = "blue";
                        ctx.fillRect(c * tileSize, r * tileSize, tileSize, tileSize);
                    } else if (map[r][c] === 2) {
                        ctx.fillStyle = "#ffb8ae";
                        ctx.beginPath();
                        ctx.arc(c * tileSize + tileSize / 2, r * tileSize + tileSize / 2, 4, 0, Math.PI * 2);
                        ctx.fill();
                    }
                }
            }

            // 팩맨 그리기
            ctx.fillStyle = "yellow";
            ctx.beginPath();
            let cx = pacman.x * tileSize + tileSize / 2;
            let cy = pacman.y * tileSize + tileSize / 2;
            ctx.arc(cx, cy, tileSize / 2 - 2, 0.2 * Math.PI, 1.8 * Math.PI);
            ctx.lineTo(cx, cy);
            ctx.fill();
        }

        function gameLoop() {
            update();
            draw();
        }

        setInterval(gameLoop, 200);
    </script>
</body>
</html>
"""

# Streamlit 내에 HTML 컴포넌트 렌더링
components.html(pacman_html, height=500)
