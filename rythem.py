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
        .ui-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 600px;
            height: 300px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            background-color: rgba(0, 0, 0, 0.7);
            z-index: 10;
        }
        .btn-container {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        .btn {
            padding: 10px 20px;
            font-size: 16px;
            font-weight: bold;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: 0.2s;
        }
        .btn-easy { background-color: #00cc66; }
        .btn-easy:hover { background-color: #00ff80; }
        .btn-hard { background-color: #ff9900; }
        .btn-hard:hover { background-color: #ffbb33; }
        .btn-extreme { background-color: #ff0055; }
        .btn-extreme:hover { background-color: #ff3377; }
        .btn-restart { background-color: #0099ff; }
        .btn-restart:hover { background-color: #33b5ff; }
        .btn-change { background-color: #888; }
        .btn-change:hover { background-color: #aaa; }
        .title-text {
            font-size: 26px;
            font-weight: bold;
            color: #fff;
            margin-bottom: 5px;
        }
        .sub-text {
            font-size: 14px;
            color: #00ffff;
            margin-bottom: 15px;
        }
    </style>
</head>
<body>
    <div style="position: relative; display: flex; justify-content: center; align-items: center;">
        <canvas id="gameCanvas" width="600" height="300"></canvas>

        <!-- 난이도 선택 (시작) 화면 -->
        <div id="startOverlay" class="ui-overlay">
            <div class="title-text">GEOMETRY DASH</div>
            <div class="sub-text">WAVE MODE - 난이도를 선택하세요</div>
            <div class="btn-container">
                <button class="btn btn-easy" onclick="selectDifficulty('easy')">1단계: 이지</button>
                <button class="btn btn-hard" onclick="selectDifficulty('hard')">2단계: 하드</button>
                <button class="btn btn-extreme" onclick="selectDifficulty('extreme')">3단계: 종결</button>
            </div>
        </div>

        <!-- 게임 오버 화면 -->
        <div id="gameOverOverlay" class="ui-overlay" style="display: none;">
            <div class="title-text" style="color: #ff3333;">GAME OVER</div>
            <div id="finalScore" class="sub-text" style="color: #fff;">SCORE: 0</div>
            <div class="btn-container">
                <button class="btn btn-restart" onclick="restartSameDifficulty()">다시 시작 🔄</button>
                <button class="btn btn-change" onclick="showDifficultySelect()">모드 변경 ⚙️</button>
            </div>
        </div>
    </div>
    <div id="info"><b>조작법:</b> 화면 클릭 또는 스페이스바 누르고 있기 (상승) / 떼기 (하강)</div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");
        const startOverlay = document.getElementById("startOverlay");
        const gameOverOverlay = document.getElementById("gameOverOverlay");
        const finalScoreText = document.getElementById("finalScore");

        // Web Audio API 설정
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

        function startBGM(speedMode) {
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
            // 종결 모드일 때는 BGM 템포도 함께 빨라짐
            let tempo = 120;
            if (speedMode === 'hard') tempo = 90;
            if (speedMode === 'extreme') tempo = 60;

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
            }, tempo);
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
        let currentMode = 'easy';
        let score = 0;
        let coinsCollected = 0;
        let gameSpeed = 5;
        let player, obstacles, coins, frameCount, animationFrameId;
        let trail = [];

        function init(mode) {
            currentMode = mode;
            isPressing = false;
            gameOver = false;
            score = 0;
            coinsCollected = 0;
            frameCount = 0;
            obstacles = [];
            coins = [];
            trail = [];

            // 난이도별 속도 설정
            if (mode === 'easy') {
                gameSpeed = 5;
            } else if (mode === 'hard') {
                gameSpeed = 8;
            } else if (mode === 'extreme') {
                gameSpeed = 14; // 종결 모드: 매 초고속 이동
            }

            player = {
                x: 80,
                y: canvas.height / 2,
                size: 10,
                speedY: gameSpeed * 0.8 // 플레이어 이동 반응성 연동
            };

            gameOverOverlay.style.display = "none";
            startOverlay.style.display = "none";
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

        function spawnElements() {
            const rand = Math.random();

            if (rand < 0.35) {
                // 1. 움직이는 톱니바퀴
                const baseCircleY = Math.random() * (canvas.height - 120) + 60;
                obstacles.push({
                    type: 'sawblade',
                    x: canvas.width,
                    baseY: baseCircleY,
                    y: baseCircleY,
                    radius: 20,
                    angle: 0,
                    moveOffset: 0,
                    moveSpeed: 0.05,
                    moveRange: 40
                });
            } else if (rand < 0.65) {
                // 2. 거대 조형물
                const gapHeight = currentMode === 'extreme' ? 100 : 85;
                const gapY = Math.random() * (canvas.height - gapHeight - 40) + 20;
                obstacles.push({
                    type: 'giant_pillar',
                    x: canvas.width,
                    width: 45,
                    gapY: gapY,
                    gapHeight: gapHeight
                });
            } else if (rand < 0.85) {
                // 3. 일반 블록 / 가시
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
                // 4. 천장/바닥 장애물
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

            const currentSpeedY = player.speedY;
            if (isPressing) {
                player.y -= currentSpeedY;
            } else {
                player.y += currentSpeedY;
            }

            // 잔상
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
            // 종결 모드일수록 장애물이 더 빠르게 스폰됨
            const spawnInterval = currentMode === 'extreme' ? 25 : (currentMode === 'hard' ? 35 : 45);
            if (frameCount % spawnInterval === 0) {
                spawnElements();
            }

            // 장애물 이동 및 충돌 판정
            for (let i = 0; i < obstacles.length; i++) {
                let obs = obstacles[i];
                obs.x -= gameSpeed;

                if (obs.type === 'block' || obs.type === 'spike') {
                    if (
                        player.x + player.size > obs.x &&
                        player.x - player.size < obs.x + obs.width &&
                        player.y + player.size > obs.y &&
                        player.y - player.size < obs.y + obs.height
                    ) {
                        triggerGameOver();
                    }
                } else if (obs.type === 'sawblade') {
                    obs.angle += 0.15;
                    obs.moveOffset += obs.moveSpeed;
                    obs.y = obs.baseY + Math.sin(obs.moveOffset) * obs.moveRange;

                    const dist = Math.hypot(player.x - obs.x, player.y - obs.y);
                    if (dist < player.size + obs.radius) {
                        triggerGameOver();
                    }
                } else if (obs.type === 'giant_pillar') {
                    if (player.x + player.size > obs.x && player.x - player.size < obs.x + obs.width) {
                        if (player.y - player.size < obs.gapY || player.y + player.size > obs.gapY + obs.gapHeight) {
                            triggerGameOver();
                        }
                    }
                }
            }

            // 코인 이동
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

            if (obstacles.length > 0 && obstacles[0].x + 60 < 0) obstacles.shift();
            while (coins.length > 0 && coins[0].x + coins[0].radius < 0) coins.shift();

            if (!gameOver) score += Math.floor(gameSpeed / 3);
        }

        function triggerGameOver() {
            gameOver = true;
            stopBGM();
            finalScoreText.innerText = "SCORE: " + score + " | COINS: " + coinsCollected;
            gameOverOverlay.style.display = "flex";
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            if (!gameStarted) return;

            // 1. 잔상
            if (trail.length > 1) {
                ctx.beginPath();
                ctx.moveTo(trail[0].x, trail[0].y);
                for (let i = 1; i < trail.length; i++) {
                    ctx.lineTo(trail[i].x, trail[i].y);
                }
                ctx.lineTo(player.x, player.y);
                ctx.strokeStyle = currentMode === 'extreme' ? "rgba(255, 0, 85, 0.8)" : (currentMode === 'hard' ? "rgba(255, 153, 0, 0.8)" : "rgba(0, 255, 255, 0.8)");
                ctx.lineWidth = 4;
                ctx.lineCap = "round";
                ctx.lineJoin = "round";
                ctx.shadowBlur = 8;
                ctx.shadowColor = currentMode === 'extreme' ? "#ff0055" : "#00ffff";
                ctx.stroke();
                ctx.shadowBlur = 0;
            }

            // 2. 장애물
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
                    ctx.save();
                    ctx.translate(obs.x, obs.y);
                    ctx.rotate(obs.angle);

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

                    ctx.fillStyle = "#9900cc";
                    ctx.beginPath();
                    ctx.arc(0, 0, obs.radius, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.strokeStyle = "#ffffff";
                    ctx.lineWidth = 2;
                    ctx.stroke();

                    ctx.fillStyle = "#111111";
                    ctx.beginPath();
                    ctx.arc(0, 0, 5, 0, Math.PI * 2);
                    ctx.fill();

                    ctx.restore();
                } else if (obs.type === 'giant_pillar') {
                    ctx.fillStyle = "#222233";
                    ctx.strokeStyle = "#00ffff";
                    ctx.lineWidth = 2;

                    ctx.fillRect(obs.x, 0, obs.width, obs.gapY);
                    ctx.strokeRect(obs.x, 0, obs.width, obs.gapY);

                    const bottomY = obs.gapY + obs.gapHeight;
                    ctx.fillRect(obs.x, bottomY, obs.width, canvas.height - bottomY);
                    ctx.strokeRect(obs.x, bottomY, obs.width, canvas.height - bottomY);

                    ctx.fillStyle = "#00ffff";
                    ctx.fillRect(obs.x, obs.gapY - 4, obs.width, 4);
                    ctx.fillRect(obs.x, bottomY, obs.width, 4);
                }
            }

            // 3. 코인
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

            // 4. 플레이어
            ctx.fillStyle = currentMode === 'extreme' ? "#ff0055" : (currentMode === 'hard' ? "#ff9900" : "#00ffff");
            ctx.beginPath();
            ctx.moveTo(player.x + player.size, player.y);
            ctx.lineTo(player.x - player.size, player.y - player.size);
            ctx.lineTo(player.x - player.size, player.y + player.size);
            ctx.closePath();
            ctx.fill();

            // UI
            ctx.fillStyle = "#ffffff";
            ctx.font = "16px sans-serif";
            ctx.textAlign = "left";
            ctx.fillText("SCORE: " + score, 15, 30);
            ctx.fillStyle = "#ffd700";
            ctx.fillText("🪙 COINS: " + coinsCollected, 150, 30);
            ctx.fillStyle = currentMode === 'extreme' ? "#ff0055" : (currentMode === 'hard' ? "#ff9900" : "#00cc66");
            const modeName = currentMode === 'extreme' ? "🔥 종결" : (currentMode === 'hard' ? "⚡ 하드" : "🌱 이지");
            ctx.fillText("MODE: " + modeName, 280, 30);
        }

        function loop() {
            update();
            draw();
            if (gameStarted && !gameOver) {
                animationFrameId = requestAnimationFrame(loop);
            }
        }

        function selectDifficulty(mode) {
            initAudio();
            if (audioCtx.state === "suspended") {
                audioCtx.resume();
            }
            gameStarted = true;
            init(mode);
            startBGM(mode);
            loop();
        }

        function restartSameDifficulty() {
            cancelAnimationFrame(animationFrameId);
            initAudio();
            if (audioCtx.state === "suspended") {
                audioCtx.resume();
            }
            init(currentMode);
            startBGM(currentMode);
            loop();
        }

        function showDifficultySelect() {
            cancelAnimationFrame(animationFrameId);
            stopBGM();
            gameStarted = false;
            gameOverOverlay.style.display = "none";
            startOverlay.style.display = "flex";
        }
    </script>
</body>
</html>
"""

# HTML 컴포넌트 렌더링
components.html(game_code, height=380)
