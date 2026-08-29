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
        let trail = [];

        // 게임 초기화 함수
        function init() {
            isPressing = false;
            gameOver = false;
            score = 0;
            frameCount = 0;
            obstacles = [];
            trail = [];

            player = {
                x: 80,
                y: canvas.height / 2,
                size: 10,
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

        // 다양한 장애물 생성 (공중 블록, 공중 가시, 천장/바닥 가시)
        function spawnObstacle() {
            const type = Math.floor(Math.random() * 3); // 0: 공중 블록, 1: 공중 가시, 2: 대형 벽
            
            if (type === 0) {
                // 공중에 떠 있는 블록
                const h = 40;
                const y = Math.random() * (canvas.height - 120) + 40;
                obstacles.push({ type: 'block', x: canvas.width, y: y, width: 35, height: h });
            } else if (type === 1) {
                // 공중에 떠 있는 가시 (삼각형)
                const y = Math.random() * (canvas.height - 100) + 50;
                obstacles.push({ type: 'spike', x: canvas.width, y: y, width: 25, height: 30 });
            } else {
                // 상단 또는 하단에 붙어있는 벽
                const isTop = Math.random() > 0.5;
                const h = Math.random() * 80 + 40;
                obstacles.push({
                    type: 'block',
                    x: canvas.width,
                    y: isTop ? 0 : canvas.height - h,
                    width: 30,
                    height: h
                });
            }
        }

        function update() {
            if (gameOver) return;

            // 위치 업데이트 (누르고 있으면 위로, 떼면 아래로)
            if (isPressing) {
                player.y -= player.speedY;
            } else {
                player.y += player.speedY;
            }

            // 잔상 위치 기록 및 이동
            const gameSpeed = 5;
            trail.push({ x: player.x, y: player.y });
            for (let i = 0; i < trail.length; i++) {
                trail[i].x -= gameSpeed;
            }
            while (trail.length > 0 && trail[0].x < 0) {
                trail.shift();
            }

            // 천장/바닥 충돌 처리
            if (player.y - player.size < 0 || player.y + player.size > canvas.height) {
                triggerGameOver();
            }

            // 장애물 생성
            frameCount++;
            if (frameCount % 45 === 0) { // 장애물 출현 간격
                spawnObstacle();
            }

            // 장애물 이동 및 충돌 체크
            for (let i = 0; i < obstacles.length; i++) {
                let obs = obstacles[i];
                obs.x -= gameSpeed;

                // 간단한 AABB 박스 충돌 판정
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
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 1. 잔상 그리기
            if (trail.length > 1) {
                ctx.beginPath();
                ctx.moveTo(trail[0].x, trail[0].y);
                for (let i = 1; i < trail.length; i++) {
                    ctx.lineTo(trail[i].x, trail[i].y);
                }
                ctx.lineTo(player.x, player.y);
                ctx.strokeStyle = "rgba(0, 255, 255, 0.8)";
                ctx.lineWidth = 4;
                ctx.lineCap = "round";
                ctx.lineJoin = "round";
                ctx.shadowBlur = 8;
                ctx.shadowColor = "#00ffff";
                ctx.stroke();
                ctx.shadowBlur = 0;
            }

            // 2. 장애물 그리기
            for (let obs of obstacles) {
                if (obs.type === 'block') {
                    // 공중/바닥 사각형 블록
                    ctx.fillStyle = "#ff0055";
                    ctx.fillRect(obs.x, obs.y, obs.width, obs.height);
                    ctx.strokeStyle = "#ffffff";
                    ctx.lineWidth = 1;
                    ctx.strokeRect(obs.x, obs.y, obs.width, obs.height);
                } else if (obs.type === 'spike') {
                    // 공중 가시 (삼각형)
                    ctx.fillStyle = "#ffaa00";
                    ctx.beginPath();
                    ctx.moveTo(obs.x, obs.y + obs.height); // 좌하단
                    ctx.lineTo(obs.x + obs.width / 2, obs.y); // 중앙 상단
                    ctx.lineTo(obs.x + obs.width, obs.y + obs.height); // 우하단
                    ctx.closePath();
                    ctx.fill();
                    ctx.strokeStyle = "#ffffff";
                    ctx.lineWidth = 1;
                    ctx.stroke();
                }
            }

            // 3. 플레이어 그리기 (화살표)
            ctx.fillStyle = "#00ffff";
            ctx.beginPath();
            ctx.moveTo(player.x + player.size, player.y);
            ctx.lineTo(player.x - player.size, player.y - player.size);
            ctx.lineTo(player.x - player.size, player.y + player.size);
            ctx.closePath();
            ctx.fill();

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
