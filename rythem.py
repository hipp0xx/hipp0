import streamlit as st
import streamlit.components.v1 as components

st.title("📐 Streamlit Geometry Dash (Wave Mode)")

# HTML/JS 기반 게임 코드
game_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0;
            background-color: #111;
            display: flex;
            justify-content: center;
            align-items: center;
            color: white;
            font-family: sans-serif;
            flex-direction: column;
        }
        canvas {
            border: 2px solid #555;
            background-color: #000;
        }
        #info {
            margin-top: 10px;
            font-size: 14px;
            color: #aaa;
        }
        #restartBtn {
            position: absolute;
            top: 200px;
            padding: 10px 20px;
            font-size: 16px;
            font-weight: bold;
            color: white;
            background-color: #ff0055;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            display: none;
            z-index: 10;
        }
        #restartBtn:hover {
            background-color: #ff3377;
        }
    </style>
</head>
<body>
    <div style="position: relative; display: flex; justify-content: center; align-items: center;">
        <canvas id="gameCanvas" width="600" height="300"></canvas>
        <button id="restartBtn" onclick="resetGame()">다시 시작 🔄</button>
    </div>
    <div id="info"><b>조작법:</b> 화면 클릭 또는 스페이스바 누르고 있기 (상승) / 떼기 (하강)</div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");
        const restartBtn = document.getElementById("restartBtn");

        // 게임 변수
        let isPressing = false;
        let gameOver = false;
        let score = 0;
        let player, obstacles, frameCount, animationFrameId;

        // 게임 초기화 함수
        function init() {
            isPressing = false;
            gameOver = false;
            score = 0;
            frameCount = 0;
            obstacles = [];

            player = {
                x: 80,
                y: canvas.height / 2,
                size: 12,
                speedY: 4
            };

            restartBtn.style.display = "none";
        }

        // 입력을 감지하는 이벤트 리스너
        window.addEventListener("keydown", (e) => {
            if (e.code === "Space") isPressing = true;
        });
        window.addEventListener("keyup", (e) => {
            if (e.code === "Space") isPressing = false;
        });
        canvas.addEventListener("mousedown", () => isPressing = true);
        canvas.addEventListener("mouseup", () => isPressing = false);

        function spawnObstacle() {
            const height = Math.random() * 120 + 30;
            const isTop = Math.random() > 0.5;
            obstacles.push({
                x: canvas.width,
                y: isTop ? 0 : canvas.height - height,
                width: 30,
                height: height
            });
        }

        function update() {
            if (gameOver) return;

            // 위치 업데이트 (누르고 있으면 위로, 떼면 아래로)
            if (isPressing) {
                player.y -= player.speedY;
            } else {
                player.y += player.speedY;
            }

            // 천장/바닥 충돌 처리
            if (player.y - player.size < 0 || player.y + player.size > canvas.height) {
                triggerGameOver();
            }

            // 장애물 생성 및 이동
            frameCount++;
            if (frameCount % 60 === 0) {
                spawnObstacle();
            }

            for (let i = 0; i < obstacles.length; i++) {
                let obs = obstacles[i];
                obs.x -= 5; // 장애물 속도

                // 플레이어와 장애물 충돌 검사
                if (
                    player.x + player.size > obs.x &&
                    player.x - player.size < obs.x + obs.width &&
                    player.y + player.size > obs.y &&
                    player.y - player.size < obs.y + obs.height
                ) {
                    triggerGameOver();
                }
            }

            // 화면을 벗어난 장애물 제거 및 점수 증가
            if (obstacles.length > 0 && obstacles[0].x + obstacles[0].width < 0) {
                obstacles.shift();
                score += 100;
            }

            if (!gameOver) score++;
        }

        function triggerGameOver() {
            gameOver = true;
            restartBtn.style.display = "block";
        }

        function draw() {
            // 배경 지우기
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 플레이어 그리기 (화살표 모양)
            ctx.fillStyle = "#00ffff";
            ctx.beginPath();
            ctx.moveTo(player.x + player.size, player.y);
            ctx.lineTo(player.x - player.size, player.y - player.size);
            ctx.lineTo(player.x - player.size, player.y + player.size);
            ctx.closePath();
            ctx.fill();

            // 장애물 그리기
            ctx.fillStyle = "#ff0055";
            for (let obs of obstacles) {
                ctx.fillRect(obs.x, obs.y, obs.width, obs.height);
            }

            // 점수 표시
            ctx.fillStyle = "#ffffff";
            ctx.font = "18px sans-serif";
            ctx.textAlign = "left";
            ctx.fillText("SCORE: " + score, 15, 30);

            // 게임 오버 메시지
            if (gameOver) {
                ctx.fillStyle = "rgba(0, 0, 0, 0.75)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = "#ff3333";
                ctx.font = "bold 30px sans-serif";
                ctx.textAlign = "center";
                ctx.fillText("GAME OVER", canvas.width / 2, canvas.height / 2 - 30);
            }
        }

        function loop() {
            update();
            draw();
            if (!gameOver) {
                animationFrameId = requestAnimationFrame(loop);
            }
        }

        function resetGame() {
            cancelAnimationFrame(animationFrameId);
            init();
            loop();
        }

        // 게임 시작
        init();
        loop();
    </script>
</body>
</html>
"""

# HTML 컴포넌트를 Streamlit 화면에 렌더링
components.html(game_code, height=380)
