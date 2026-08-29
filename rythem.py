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
        .btn {
            position: absolute;
            top: 180px;
            padding: 12px 28px;
            font-size: 18px;
            font-weight: bold;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            z-index: 10;
        }
        #startBtn {
            background-color: #00cc66;
        }
        #startBtn:hover {
            background-color: #00ff80;
        }
        #restartBtn {
            background-color: #ff0055;
            display: none;
        }
        #restartBtn:hover {
            background-color: #ff3377;
        }
    </style>
</head>
<body>
    <div style="position: relative; display: flex; justify-content: center; align-items: center;">
        <canvas id="gameCanvas" width="600" height="300"></canvas>
        <button id="startBtn" class="btn" onclick="startGame()">게임 시작 ▶</button>
        <button id="restartBtn" class="btn" onclick="resetGame()">다시 시작 🔄</button>
    </div>
    <div id="info"><b>조작법:</b> 화면 클릭 또는 스페이스바 누르고 있기 (상승) / 떼기 (하강)</div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");
        const startBtn = document.getElementById("startBtn");
        const restartBtn = document.getElementById("restartBtn");

        // Web Audio API 설정 (피아노 + 바이올린 BGM)
        let audioCtx = null;
        let bgmInterval = null;

        function initAudio() {
            if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            }
        }

        const FREQS = {
            A2: 110.00, C3: 130.81, E3: 164.81, G3: 196.00,
            A3: 220.00, C4: 261.63, E4: 329.63, F4: 349.23,
            G4: 392.00, A4: 440.00, B4: 493.88, C5: 523.25, E5: 659.25
        };

        function playPiano(freq, time, duration = 0.25) {
            if (!audioCtx) return;
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();

            osc.type = "triangle";
            osc.frequency.setValueAtTime(freq, time);

            gain.gain.setValueAtTime(0.15, time);
            gain.gain.exponentialRampToValueAtTime(0.001, time + duration);

            osc.connect(gain);
            gain.connect(audioCtx.destination);

            osc.start(time);
            osc.stop(time + duration);
        }

        function playViolin(freq, time, duration = 0.5) {
            if (!audioCtx) return;
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            const lfo = audioCtx.createOscillator();
            const lfoGain = audioCtx.createGain();

            osc.type = "sawtooth";
            osc.frequency.setValueAtTime(freq, time);

            lfo.frequency.setValueAtTime(6, time);
            lfoGain.gain.setValueAtTime(3, time);
            lfo.connect(osc.frequency);

            gain.gain.setValueAtTime(0.01, time);
            gain.gain.linearRampToValueAtTime(0.08, time + 0.1);
            gain.gain.exponentialRampToValueAtTime(0.001, time + duration);

            osc.connect(gain);
            gain.connect(audioCtx.destination);

            lfo.start(time);
            osc.start(time);
            
            lfo.stop(time + duration);
            osc.stop(time + duration);
        }

        function startBGM() {
            if (!audioCtx) return;
            stopBGM();

            const pianoMelody = [
                FREQS.A4, FREQS.C5, FREQS.E5, FREQS.C5,
                FREQS.G4, FREQS.B4, FREQS.E5, FREQS.B4,
                FREQS.F4, FREQS.A4, FREQS.C5, FREQS.A4,
                FREQS.E4, FREQS.G4, FREQS.B4, FREQS.G4
            ];

            const violinChords = [
                FREQS.A4, FREQS.G4, FREQS.F4, FREQS.E4
            ];

            let step = 0;

            bgmInterval = setInterval(() => {
                if (!audioCtx || audioCtx.state === "suspended") return;

                const now = audioCtx.currentTime;

                const pFreq = pianoMelody[step % pianoMelody.length];
                playPiano(pFreq, now, 0.2);

                if (step % 4 === 0) {
                    const vFreq = violinChords[Math.floor(step / 4) % violinChords.length];
                    playViolin(vFreq, now, 0.6);
                }

                step++;
            }, 120);
        }

        function stopBGM() {
            if (bgmInterval) {
                clearInterval(bgmInterval);
                bgmInterval = null;
            }
        }

        // 게임 변수
        let isPressing = false;
        let gameStarted = false;
        let gameOver = false;
        let score = 0;
        let coinsCollected = 0;
        let gameSpeed = 5;
        let player, obstacles, coins, portals, frameCount, animationFrameId;
        let trail = [];

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

        // 입력 이벤트
        window.addEventListener("keydown", (e) => {
            if (e.code === "Space") isPressing = true;
        });
        window.addEventListener("keyup", (e) => {
            if (e.code === "Space") isPressing = false;
        });
        canvas.addEventListener("mousedown", () => isPressing = true);
        canvas.addEventListener("mouseup", () => isPressing = false);

        // 장애물 생성 알고리즘 (다양한 타입 지원)
        function spawnElements() {
            const rand = Math.random();

            if (rand < 0.20) {
                // 1. 배속 포탈
                const isFast = gameSpeed <= 5;
                portals.push({
                    x: canvas.width,
                    y: Math.random() * (canvas.height - 100) + 50,
                    width: 20,
                    height: 60,
                    type: isFast ? 'fast' : 'slow',
                    active: true
                });
            } else if (rand < 0.40) {
                // 2. [NEW] 움직이는 톱니바퀴 (Sawblade)
                const baseCircleY = Math.random() * (canvas.height - 120) + 60;
                obstacles.push({
                    type: 'sawblade',
                    x: canvas.width,
                    baseY: baseCircleY,
                    y: baseCircleY,
                    radius: 20,
                    angle: 0,
                    moveOffset: 0,
                    moveSpeed: 0.05, // 상하 움직임 속도
                    moveRange: 40    // 상하 움직임 범위
                });
            } else if (rand < 0.60) {
                // 3. [NEW] 거대한 구조물 (Gate/Giant Pillar - 중앙 통로 제외 통곡의 벽)
                const gapHeight = 90; // 통과할 공간
                const gapY = Math.random() * (canvas.height - gapHeight - 40) + 20;
                obstacles.push({
                    type: 'giant_pillar',
                    x: canvas.width,
                    width: 45,
                    gapY: gapY,
                    gapHeight: gapHeight
                });
            } else if (rand < 0.80) {
                // 4. 일반 블록 / 가시
                const isSpike = Math.random() > 0.5;
                if (isSpike) {
                    const y = Math.random() * (canvas.height - 100) + 50;
                    obstacles.push({ type: 'spike', x: canvas.width, y: y, width: 25, height: 30 });
                } else {
                    const h = 40;
                    const y = Math.random() * (canvas.height - 120) + 40;
                    obstacles.push({ type: 'block', x: canvas.width, y: y, width: 35, height: h });
                }
            } else {
                // 5. 天/地 블록
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

            // 골드 코인 생성
            if (Math.random() > 0.5) {
                const coinY = Math.random() * (canvas.height - 80) + 40;
                coins.push({
                    x: canvas.width + 50,
                    y: coinY,
                    radius: 8,
                    collected: false
                });
            }
        }

        function update() {
            if (!gameStarted || gameOver) return;

            const currentSpeedY = player.speedY * (gameSpeed / 5);
            if (isPressing) {
                player.y -= currentSpeedY;
            } else {
                player.y += currentSpeedY;
            }

            // 플레이어 잔상
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

            frameCount++;
            if (frameCount % 45 === 0) {
                spawnElements();
            }

            // 장애물 업데이트 및 충돌 검사
            for (let i = 0; i < obstacles.length; i++) {
                let obs = obstacles[i];
                obs.x -= gameSpeed;

                if (obs.type === 'block') {
                    if (
                        player.x + player.size > obs.x &&
                        player.x - player.size < obs.x + obs.width &&
                        player.y + player.size > obs.y &&
                        player.y - player.size < obs.y + obs.height
                    ) {
                        triggerGameOver();
                    }
                } else if (obs.type === 'spike') {
                    if (
                        player.x + player.size > obs.x &&
                        player.x - player.size < obs.x + obs.width &&
                        player.y + player.size > obs.y &&
                        player.y - player.size < obs.y + obs.height
                    ) {
                        triggerGameOver();
                    }
                } else if (obs.type === 'sawblade') {
                    // 톱니바퀴 자체 회전 및 위아래 상하운동
                    obs.angle += 0.1;
                    obs.moveOffset += obs.moveSpeed;
                    obs.y = obs.baseY + Math.sin(obs.moveOffset) * obs.moveRange;

                    // 원형-원형 충돌 판정
                    const dist = Math.hypot(player.x - obs.x, player.y - obs.y);
                    if (dist < player.size + obs.radius) {
                        triggerGameOver();
                    }
                } else if (obs.type === 'giant_pillar') {
                    // 거대 조형물 (통로 공간 외의 상/하 기둥과 충돌)
                    if (player.x + player.size > obs.x && player.x - player.size < obs.x + obs.width) {
                        if (player.y - player.size < obs.gapY || player.y + player.size > obs.gapY + obs.gapHeight) {
                            triggerGameOver();
                        }
                    }
                }
            }

            // 포탈 업데이트
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
                    gameSpeed = p.type === 'fast' ? 8 : 5;
                }
            }

            // 코인 업데이트
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

            // 화면을 벗어난 장애물 정리
            if (obstacles.length > 0 && obstacles[0].x + 60 < 0) obstacles.shift();
            if (portals.length > 0 && portals[0].x + portals[0].width < 0) portals.shift();
            while (coins.length > 0 && coins[0].x + coins[0].radius < 0) coins.shift();

            if (!gameOver) score += Math.floor(gameSpeed / 5);
        }

        function triggerGameOver() {
            gameOver = true;
            stopBGM();
            restartBtn.style.display = "block";
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            if (!gameStarted) {
                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 28px sans-serif";
                ctx.textAlign = "center";
                ctx.fillText("GEOMETRY DASH", canvas.width / 2, canvas.height / 2 - 40);
                ctx.font = "16px sans-serif";
                ctx.fillStyle = "#00ffff";
                ctx.fillText("WAVE MODE", canvas.width / 2, canvas.height / 2 - 10);
                return;
            }

            // 1. 웨이브 잔상
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

            // 2. 포탈
            for (let p of portals) {
                if (p.active) {
                    ctx.fillStyle = p.type === 'fast' ? '#ff6600' : '#0088ff';
                    ctx.fillRect(p.x, p.y, p.width, p.height);
                    ctx.strokeStyle = '#ffffff';
                    ctx.lineWidth = 2;
                    ctx.strokeRect(p.x, p.y, p.width, p.height);
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
                } else if (obs.type === 'sawblade') {
                    // [NEW] 움직이는 회전 톱니바퀴
                    ctx.save();
                    ctx.translate(obs.x, obs.y);
                    ctx.rotate(obs.angle);

                    // 톱니 이빨
                    ctx.fillStyle = "#bb00ff";
                    const teeth = 8;
                    for (let i = 0; i < teeth; i++) {
                        ctx.rotate((Math.PI * 2) / teeth);
                        ctx.beginPath();
                        ctx.moveTo(0, -obs.radius - 5);
                        ctx.lineTo(5, -obs.radius + 3);
                        ctx.lineTo(-5, -obs.radius + 3);
                        ctx.closePath();
                        ctx.fill();
                    }

                    // 톱니 원형 몸통
                    ctx.fillStyle = "#9900cc";
                    ctx.beginPath();
                    ctx.arc(0, 0, obs.radius, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.strokeStyle = "#ffffff";
                    ctx.lineWidth = 2;
                    ctx.stroke();

                    // 중앙 구멍
                    ctx.fillStyle = "#111111";
                    ctx.beginPath();
                    ctx.arc(0, 0, 5, 0, Math.PI * 2);
                    ctx.fill();

                    ctx.restore();
                } else if (obs.type === 'giant_pillar') {
                    // [NEW] 거대 구조물 (위/아래 기둥)
                    ctx.fillStyle = "#222233";
                    ctx.strokeStyle = "#00ffff";
                    ctx.lineWidth = 2;

                    // 위쪽 기둥
                    ctx.fillRect(obs.x, 0, obs.width, obs.gapY);
                    ctx.strokeRect(obs.x, 0, obs.width, obs.gapY);

                    // 아래쪽 기둥
                    const bottomY = obs.gapY + obs.gapHeight;
                    ctx.fillRect(obs.x, bottomY, obs.width, canvas.height - bottomY);
                    ctx.strokeRect(obs.x, bottomY, obs.width, canvas.height - bottomY);

                    // 테두리 강조
                    ctx.fillStyle = "#00ffff";
                    ctx.fillRect(obs.x, obs.gapY - 4, obs.width, 4);
                    ctx.fillRect(obs.x, bottomY, obs.width, 4);
                }
            }

            // 4. 코인
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

            // 5. 플레이어 (화살표 모양)
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
            ctx.fillStyle = gameSpeed > 5 ? "#ff6600" : "#0088ff";
            ctx.fillText(gameSpeed > 5 ? "⚡ FAST" : "🐢 NORMAL", 280, 30);

            // 게임 오버
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
            if (gameStarted && !gameOver) {
                animationFrameId = requestAnimationFrame(loop);
            }
        }

        function startGame() {
            initAudio();
            if (audioCtx.state === "suspended") {
                audioCtx.resume();
            }
            startBtn.style.display = "none";
            gameStarted = true;
            init();
            startBGM();
            loop();
        }

        function resetGame() {
            cancelAnimationFrame(animationFrameId);
            initAudio();
            if (audioCtx.state === "suspended") {
                audioCtx.resume();
            }
            init();
            startBGM();
            loop();
        }

        draw();
    </script>
</body>
</html>
"""

# HTML 컴포넌트 렌더링
components.html(game_code, height=380)
