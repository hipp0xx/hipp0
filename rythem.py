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
        let coinsCollected = 0;
        let gameSpeed = 5; // 기본 이동 속도
        let player, obstacles, coins, portals, frameCount, animationFrameId;
        let trail = [];

        // 게임 초기화 함수
        function init() {
            isPressing = false;
            gameOver = false;
            score = 0;
            coinsCollected = 0;
            gameSpeed = 5;
            frameCount = 0;
            obstacles = [];
            coins = [];
            portals = [];
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

        // 요소 생성 (장애물, 코인, 포탈)
        function spawnElements() {
            const rand = Math.random();

            if (rand < 0.25) {
                // 속도 변경 포탈 생성
                const isFast = gameSpeed <= 5; // 현재 느리면 가속 포탈, 빠르면 감속 포탈 유도
                portals.push({
                    x: canvas.width,
                    y: Math.random() * (canvas.height - 100) + 50,
                    width: 20,
                    height: 60,
                    type: isFast ? 'fast' : 'slow',
                    active: true
                });
            } else if (rand < 0.6) {
                // 공중/바닥 장애물
                const type = Math.floor(Math.random() * 2);
                if (type === 0) {
                    const h = 40;
                    const y = Math.random() * (canvas.height - 120) + 40;
                    obstacles.push({ type: 'block', x: canvas.width, y: y, width: 35, height: h });
                } else {
                    const y = Math.random() * (canvas.height - 100) + 50;
                    obstacles.push({ type: 'spike', x: canvas.width, y: y, width: 25, height: 30 });
                }
            } else {
                // 천장/바닥 벽
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

            // 코인 생성
            if (Math.random() > 0.6) {
                const coinY = Math.random() * (canvas.height - 80) + 40;
                coins.push({
                    x: canvas.width + 40,
                    y: coinY,
                    radius: 8,
                    collected: false
                });
            }
        }

        function update() {
            if (gameOver) return;

            // 위치 업데이트 (속도에 맞춰 상하 이동 속도도 약간 조절)
            const currentSpeedY = player.speedY * (gameSpeed / 5);
            if (isPressing) {
                player.y -= currentSpeedY;
            } else {
                player.y += currentSpeedY;
            }

            // 잔상 이동
            trail.push({ x: player.x, y: player.y });
            for (let i = 0; i < trail.length; i++) {
                trail[i].x -= gameSpeed;
            }
            while (trail.length > 0 && trail[0].x < 0) {
                trail.shift();
            }

            // 천장/바닥 충돌
            if (player.y - player.size < 0 || player.y + player.size > canvas.height) {
                triggerGameOver();
            }

            // 요소 생성
            frameCount++;
            if (frameCount % 45 === 0) {
                spawnElements();
            }

            // 장애물 이동 및 충돌
            for (let i = 0; i < obstacles.length; i++) {
                let obs = obstacles[i];
                obs.x -= gameSpeed;

                if (
                    player.x + player.size > obs.x &&
                    player.x - player.size < obs.x + obs.width &&
                    player.y + player.size > obs.y &&
                    player.y - player.size < obs.y + obs.height
                ) {
                    triggerGameOver();
                }
            }

            // 포탈 이동 및 통과 처리
            for (let i = 0; i < portals.length; i++) {
                let p = portals[i];
                p.x -= gameSpeed;

                if (p.active &&
                    player.x + player.size > p.x &&
                    player.x - player.size < p.x + p.width &&
                    player.y + player.size > p.y &&
                    player.y - player.size < p.y + p.height
                ) {
                    p.active = false;
                    if (p.type === 'fast') {
                        gameSpeed = 8; // 속도 증가
                    } else {
                        gameSpeed = 5; // 속도 감속 (기본)
                    }
                }
            }

            // 코인 이동 및 획득
            for (let i = 0; i < coins.length; i++) {
                let coin = coins[i];
                coin.x -= gameSpeed;

                if (!coin.collected) {
                    const dist = Math.hypot(player.x - coin.x, player.y - coin.y);
                    if (dist < player.size + coin.radius) {
                        coin.collected = true;
                        score += 500;
                        coinsCollected++;
                    }
                }
            }

            // 배열 정리
            if (obstacles.length > 0 && obstacles[0].x + obstacles[0].width < 0) obstacles.shift();
            if (portals.length > 0 && portals[0].x + portals[0].width < 0) portals.shift();
            while (coins.length > 0 && coins[0].x + coins[0].radius < 0) coins.shift();

            if (!gameOver) score += Math.floor(gameSpeed / 5);
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
                ctx.strokeStyle = gameSpeed > 5 ? "rgba(255, 100, 0, 0.8)" : "rgba(0, 255, 255, 0.8)";
                ctx.lineWidth = 4;
                ctx.lineCap = "round";
                ctx.lineJoin = "round";
                ctx.shadowBlur = 8;
                ctx.shadowColor = gameSpeed > 5 ? "#ff6400" : "#00ffff";
                ctx.stroke();
                ctx.shadowBlur = 0;
            }

            // 2. 포탈 그리기
            for (let p of portals) {
                if (p.active) {
                    ctx.fillStyle = p.type === 'fast' ? '#ff6600' : '#0088ff';
                    ctx.fillRect(p.x, p.y, p.width, p.height);
                    ctx.strokeStyle = '#ffffff';
                    ctx.lineWidth = 2;
                    ctx.strokeRect(p.x, p.y, p.width, p.height);

                    // 포탈 내부 효과 (타원)
                    ctx.fillStyle = '#ffffff';
                    ctx.beginPath();
                    ctx.ellipse(p.x + p.width / 2, p.y + p.height / 2, 4, p.height / 3, 0, 0, Math.PI * 2);
                    ctx.fill();
                }
            }

            // 3. 장애물 그리기
            for (let obs of obstacles) {
                if (obs.type === 'block') {
                    ctx.fillStyle = "#ff0055";
                    ctx.fillRect(obs.x, obs.y, obs.width, obs.height);
                    ctx.strokeStyle = "#ffffff";
                    ctx.lineWidth = 1;
                    ctx.strokeRect(obs.x, obs.y, obs.width, obs.height);
                } else if (obs.type === 'spike') {
                    ctx.fillStyle = "#ffaa00";
                    ctx.beginPath();
                    ctx.moveTo(obs.x, obs.y + obs.height);
                    ctx.lineTo(obs.x + obs.width / 2, obs.y);
                    ctx.lineTo(obs.x + obs.width, obs.y + obs.height);
                    ctx.closePath();
                    ctx.fill();
                    ctx.strokeStyle = "#ffffff";
                    ctx.lineWidth = 1;
                    ctx.stroke();
                }
            }

            // 4. 코인 그리기
            for (let coin of coins) {
                if (!coin.collected) {
                    ctx.fillStyle = "#ffd700";
                    ctx.beginPath();
                    ctx.arc(coin.x, coin.y, coin.radius, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.strokeStyle = "#ffffff";
                    ctx.lineWidth = 1.5;
                    ctx.stroke();
                }
            }

            // 5. 플레이어 그리기
            ctx.fillStyle = gameSpeed > 5 ? "#ffcc00" : "#00ffff";
            ctx.beginPath();
            ctx.moveTo(player.x + player.size, player.y);
            ctx.lineTo(player.x - player.size, player.y - player.size);
            ctx.lineTo(player.x - player.size, player.y + player.size);
            ctx.closePath();
            ctx.fill();

            // UI 표시
            ctx.fillStyle = "#ffffff";
            ctx.font = "16px sans-serif";
            ctx.textAlign = "left";
            ctx.fillText("SCORE: " + score, 15, 30);
            ctx.fillStyle = "#ffd700";
            ctx.fillText("🪙 COINS: " + coinsCollected, 150, 30);

            // 현재 속도 상태 표시
            ctx.fillStyle = gameSpeed > 5 ? "#ff6600" : "#0088ff";
            ctx.fillText(gameSpeed > 5 ? "⚡ FAST" : "🐢 NORMAL", 280, 30);

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
