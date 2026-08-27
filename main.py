import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Streamlit Pac-Man Large", layout="centered")

st.title("🟡 Streamlit 대형 팩맨 게임")
st.write("방향키(⬆️ ⬇️ ⬅️ ➡️)를 사용해 맵 전체의 쿠키를 모두 먹으세요!")

pacman_large_html = """
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
            color: yellow;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div id="score">SCORE: <span id="scoreVal">0</span></div>
    <canvas id="canvas" width="500" height="500"></canvas>

    <script>
        const canvas = document.getElementById("canvas");
        const ctx = canvas.getContext("2d");
        const scoreElem = document.getElementById("scoreVal");

        // 20x20 맵에 맞춰 타일 크기를 25px로 설정 (20 * 25 = 500px)
        const tileSize = 25;
        let score = 0;

        // 1: 벽, 2: 쿠키, 0: 빈 공간
        const map = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 1],
            [1, 2, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 2, 1],
            [1, 2, 1, 1, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 1, 1, 2, 1],
            [1, 2, 2, 2, 2, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 2, 2, 2, 2, 1],
            [1, 1, 1, 1, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 1, 1, 1, 1],
            [1, 2, 2, 2, 2, 1, 2, 1, 1, 0, 0, 1, 1, 2, 1, 2, 2, 2, 2, 1],
            [1, 2, 1, 1, 2, 2, 2, 1, 0, 0, 0, 0, 1, 2, 2, 2, 1, 1, 2, 1],
            [1, 2, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 2, 1],
            [1, 2, 2, 2, 2, 1, 2, 2, 2, 0, 0, 2, 2, 2, 1, 2, 2, 2, 2, 1],
            [1, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1],
            [1, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 1],
            [1, 1, 2, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 2, 1, 1],
            [1, 2, 2, 2, 2, 1, 2, 2, 2, 1, 1, 2, 2, 2, 1, 2, 2, 2, 2, 1],
            [1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ];

        let pacman = { x: 1, y: 1, dx: 0, dy: 0 };
        let ghost = { x: 18, y: 17, dx: -1, dy: 0 };

        document.addEventListener("keydown", (e) => {
            if (e.key === "ArrowUp") { pacman.dx = 0; pacman.dy = -1; }
            else if (e.key === "ArrowDown") { pacman.dx = 0; pacman.dy = 1; }
            else if (e.key === "ArrowLeft") { pacman.dx = -1; pacman.dy = 0; }
            else if (e.key === "ArrowRight") { pacman.dx = 1; pacman.dy = 0; }
        });

        function update() {
            // 팩맨 이동
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

            // 간단한 유령 랜덤 이동 로직
            const directions = [{dx:0, dy:-1}, {dx:0, dy:1}, {dx:-1, dy:0}, {dx:1, dy:0}];
            let validMoves = directions.filter(d => {
                let gx = ghost.x + d.dx;
                let gy = ghost.y + d.dy;
                return map[gy] && map[gy][gx] !== 1;
            });

            if (validMoves.length > 0) {
                let move = validMoves[Math.floor(Math.random() * validMoves.length)];
                ghost.x += move.dx;
                ghost.y += move.dy;
            }

            // 충돌 체크
            if (pacman.x === ghost.x && pacman.y === ghost.y) {
                alert("게임 오버! 점수: " + score);
                pacman.x = 1;
                pacman.y = 1;
                pacman.dx = 0;
                pacman.dy = 0;
                score = 0;
                scoreElem.innerText = score;
            }
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 맵 그리기
            for (let r = 0; r < map.length; r++) {
                for (let c = 0; c < map[r].length; c++) {
                    if (map[r][c] === 1) {
                        ctx.fillStyle = "#1919A6";
                        ctx.fillRect(c * tileSize, r * tileSize, tileSize, tileSize);
                    } else if (map[r][c] === 2) {
                        ctx.fillStyle = "#ffb8ae";
                        ctx.beginPath();
                        ctx.arc(c * tileSize + tileSize / 2, r * tileSize + tileSize / 2, 3, 0, Math.PI * 2);
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

            // 유령 그리기 (빨간색)
            ctx.fillStyle = "red";
            ctx.beginPath();
            let gx = ghost.x * tileSize + tileSize / 2;
            let gy = ghost.y * tileSize + tileSize / 2;
            ctx.arc(gx, gy, tileSize / 2 - 2, 0, Math.PI * 2);
            ctx.fill();
        }

        function gameLoop() {
            update();
            draw();
        }

        setInterval(gameLoop, 150);
    </script>
</body>
</html>
"""

components.html(pacman_large_html, height=600)
