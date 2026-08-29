import streamlit as st
import streamlit.components.v1 as components

st.title("📐 Streamlit Geometry Dash (Classic Jump Mode)")

# HTML/JS 기반 클래식 점프맵 게임 코드
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
            background-color: rgba(0, 0, 0, 0.75);
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

        <!-- 난이도 선택 화면 -->
        <div id="startOverlay" class="ui-overlay">
            <div class="title-text">GEOMETRY DASH</div>
            <div class="sub-text">JUMP MAP - 난이도를 선택하세요</div>
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
    <div id="info"><b>조작법:</b> 화면 클릭, 스페이스바 또는 위쪽 화살표 (점프)</div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");
        const startOverlay = document.getElementById("startOverlay");
        const gameOverOverlay = document.getElementById("gameOverOverlay");
        const finalScoreText = document.getElementById("finalScore");

        const FLOOR_Y = 240; // 바닥 높이

        // Web Audio API BGM
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

        // 게임 물리 및 상태 변수
        let gameStarted = false;
        let gameOver = false;
        let currentMode = 'easy';
        let score = 0;
        let coinsCollected = 0;
        let gameSpeed = 5;
        let gravity = 0.7;
        let jumpForce = -12;
        let player, obstacles, coins, frameCount, animationFrameId;

        function init(mode) {
            currentMode = mode;
            gameOver = false;
            score = 0;
            coinsCollected = 0;
            frameCount = 0;
            obstacles = [];
            coins = [];

            if (mode === 'easy') {
                gameSpeed = 5;
                gravity = 0.65;
                jumpForce = -11.5;
            } else if (mode === 'hard') {
                gameSpeed = 8;
                gravity = 0.85;
                jumpForce = -13.5;
            } else if (mode === 'extreme') {
                gameSpeed = 13;
                gravity = 1.1;
                jumpForce = -15.5;
            }

            player = {
                x: 80,
                y: FLOOR_Y - 30,
                width: 30,
                height: 30,
                vy: 0,
                isGrounded: true,
                rotation: 0
            };

            gameOverOverlay.style.display = "none";
            startOverlay.style.display = "none";
        }

        function jump() {
            if (player.isGrounded && gameStarted && !gameOver) {
                player.vy = jumpForce;
                player.isGrounded = false;
            }
        }

        // 입력 처리 (점프)
        window.addEventListener("keydown", (e) => {
            if (e.code === "Space" || e.code === "ArrowUp") jump();
        });
        canvas.addEventListener("mousedown", jump);

        // 장애물 스폰 함수 (가시, 계단, 단독 블록)
        function spawnElements() {
            const rand = Math.random();

            if (rand < 0.35) {
                // 1. 단일 가시 또는 연달아 있는 가시 (1~3개)
                const spikeCount = currentMode === 'extreme' ? Math.floor(Math.random() * 3) + 1 : (Math.random() > 0.5 ? 2 : 1);
                for (let i = 0; i < spikeCount; i++) {
                    obstacles.push({
                        type: 'spike',
                        x: canvas.width + (i * 25),
                        y: FLOOR_Y - 30,
                        width: 25,
                        height: 30
                    });
                }
            } else if (rand < 0.7) {
                // 2. 계단식 밟기 블록 구조 (Stairs)
                const stepCount = Math.floor(Math.random() * 2) + 2; // 2~3단 계단
                const blockWidth = 35;
                const blockHeight = 25;

                for (let i = 0; i < stepCount; i++) {
                    obstacles.push({
                        type: 'block',
                        x: canvas.width + (i * blockWidth),
                        y: FLOOR_Y - ((i + 1) * blockHeight),
                        width: blockWidth,
                        height: (i + 1) * blockHeight
                    });
                }
            } else {
                // 3. 높은 가공 발판 (공중 블록)
                const blockY = FLOOR_Y - (Math.random() * 40 + 50);
                obstacles.push({
                    type: 'block',
                    x: canvas.width,
                    y: blockY,
                    width: 60,
                    height: 20
                });

                // 발판 위에 코인 배치
                coins.push({
                    x: canvas.width + 30,
                    y: blockY - 20,
                    radius: 8,
                    collected: false
                });
            }

            // 일반 길목 코인 스폰
            if (Math.random() > 0.6 && rand < 0.7) {
                coins.push({
                    x: canvas.width + 10,
                    y: FLOOR_Y - 70,
                    radius: 8,
                    collected: false
                });
            }
        }

        function update() {
            if (!gameStarted || gameOver) return;

            // 중력 적용
            player.vy += gravity;
            player.y += player.vy;

            // 회전 애니메이션 (공중에 떠있을 때 사각형이 90도씩 회전)
            if (!player.isGrounded) {
                player.rotation += 0.12;
            } else {
                // 바닥에 착지 시 직각으로 정렬
                player.rotation = Math.round(player.rotation / (Math.PI / 2)) * (Math.PI / 2);
            }

            // 기본 바닥 착지 처리
            player.isGrounded = false;
            if (player.y + player.height >= FLOOR_Y) {
                player.y = FLOOR_Y - player.height;
                player.vy = 0;
                player.isGrounded = true;
            }

            frameCount++;
            const spawnInterval = currentMode === 'extreme' ? 35 : (currentMode === 'hard' ? 45 : 60);
            if (frameCount % spawnInterval === 0) {
                spawnElements();
            }

            // 장애물 이동 및 충돌 판정
            for (let i = 0; i < obstacles.length; i++) {
                let obs = obstacles[i];
                obs.x -= gameSpeed;

                if (obs.type === 'spike') {
                    // 가시 충돌 (사각-삼각 충돌 판정 간소화)
                    if (
                        player.x + player.width > obs.x + 4 &&
                        player.x < obs.x + obs.width - 4 &&
                        player.y + player.height > obs.y + 4
                    ) {
                        triggerGameOver();
                    }
                } else if (obs.type === 'block') {
                    // 블록 충돌 및 밟기 판정
                    const pRight = player.x + player.width;
                    const pLeft = player.x;
                    const pBottom = player.y + player.height;
                    const pTop = player.y;

                    const oRight = obs.x + obs.width;
                    const oLeft = obs.x;
                    const oBottom = obs.y + obs.height;
                    const oTop = obs.y;

                    if (pRight > oLeft && pLeft < oRight && pBottom > oTop && pTop < oBottom) {
                        // 위에서 블록을 밟았을 경우
                        if (player.vy >= 0 && pBottom - player.vy <= oTop + 8) {
                            player.y = oTop - player.height;
                            player.vy = 0;
                            player.isGrounded = true;
                        } else {
                            // 옆이나 밑에서 정면 충돌 시 사망
                            triggerGameOver();
                        }
                    }
                }
            }

            // 코인 이동 및 획득
            for (let i = 0; i < coins.length; i++) {
                let coin = coins[i];
                coin.x -= gameSpeed;

                if (!coin.collected) {
                    const dist = Math.hypot((player.x + player.width / 2) - coin.x, (player.y + player.height / 2) - coin.y);
                    if (dist < player.width / 2 + coin.radius) {
                        coin.collected = true;
                        score += 500;
                        coinsCollected++;
                    }
                }
            }

            // 화면 벗어난 오브젝트 삭제
            if (obstacles.length > 0 && obstacles[0].x + 100 < 0) obstacles.shift();
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

            // 1. 바닥 배경 라인
            ctx.fillStyle = "#222233";
            ctx.fillRect(0, FLOOR_Y, canvas.width, canvas.height - FLOOR_Y);
            ctx.strokeStyle = "#00ffff";
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.moveTo(0, FLOOR_Y);
            ctx.lineTo(canvas.width, FLOOR_Y);
            ctx.stroke();

            // 2. 장애물 (가시, 계단/블록)
            for (let obs of obstacles) {
                if (obs.type === 'spike') {
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
                } else if (obs.type === 'block') {
                    ctx.fillStyle = "#0088ff";
                    ctx.fillRect(obs.x, obs.y, obs.width, obs.height);
                    ctx.strokeStyle = "#ffffff";
                    ctx.lineWidth = 1.5;
                    ctx.strokeRect(obs.x, obs.y, obs.width, obs.height);
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

            // 4. 플레이어 (회전하는 큐브)
            ctx.save();
            ctx.translate(player.x + player.width / 2, player.y + player.height / 2);
            ctx.rotate(player.rotation);

            // 큐브 몸통
            ctx.fillStyle = currentMode === 'extreme' ? "#ff0055" : (currentMode === 'hard' ? "#ff9900" : "#00ffcc");
            ctx.fillRect(-player.width / 2, -player.height / 2, player.width, player.height);
            ctx.strokeStyle = "#ffffff";
            ctx.lineWidth = 2;
            ctx.strokeRect(-player.width / 2, -player.height / 2, player.width, player.height);

            // 큐브 눈 장식
            ctx.fillStyle = "#111";
            ctx.fillRect(-6, -6, 4, 4);
            ctx.fillRect(2, -6, 4, 4);

            ctx.restore();

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
