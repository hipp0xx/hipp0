import streamlit as st
import streamlit.components.v1 as components

st.title("📐 Streamlit Geometry Dash (Spaced Jump Edition)")

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
        .btn-start { background-color: #00cc66; }
        .btn-start:hover { background-color: #00ff80; }
        .btn-restart { background-color: #0099ff; }
        .btn-restart:hover { background-color: #33b5ff; }
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

        <!-- 시작 화면 -->
        <div id="startOverlay" class="ui-overlay">
            <div class="title-text">GEOMETRY DASH</div>
            <div class="sub-text">넓은 계단 점프 액션</div>
            <div class="btn-container">
                <button class="btn btn-start" onclick="startGame()">게임 시작 🚀</button>
            </div>
        </div>

        <!-- 게임 오버 화면 -->
        <div id="gameOverOverlay" class="ui-overlay" style="display: none;">
            <div class="title-text" style="color: #ff3333;">GAME OVER</div>
            <div id="finalScore" class="sub-text" style="color: #fff;">SCORE: 0</div>
            <div class="btn-container">
                <button class="btn btn-restart" onclick="restartGame()">다시 시작 🔄</button>
            </div>
        </div>
    </div>
    <div id="info"><b>조작법:</b> 스페이스바, 위쪽 화살표 또는 클릭 (길게 누르면 연속 점프 유지)</div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");
        const startOverlay = document.getElementById("startOverlay");
        const gameOverOverlay = document.getElementById("gameOverOverlay");
        const finalScoreText = document.getElementById("finalScore");

        const FLOOR_Y = 240;

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
            let tempo = 120;

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

        // 게임 상태 및 물리 변수 (이지 모드 고정)
        let gameStarted = false;
        let gameOver = false;
        let score = 0;
        let coinsCollected = 0;
        const gameSpeed = 5;
        const gravity = 0.58;
        const jumpForce = -9.2;

        let player, obstacles, terrains, coins, frameCount, animationFrameId;
        let isJumpHolding = false; // 버튼 홀드 상태 변수

        function init() {
            gameOver = false;
            score = 0;
            coinsCollected = 0;
            frameCount = 0;
            obstacles = [];
            terrains = [];
            coins = [];

            player = {
                x: 80,
                y: FLOOR_Y - 26,
                width: 26,
                height: 26,
                vy: 0,
                isGrounded: true,
                rotation: 0
            };

            gameOverOverlay.style.display = "none";
            startOverlay.style.display = "none";
        }

        // 키/마우스 입력 이벤트 (홀드 처리)
        window.addEventListener("keydown", (e) => {
            if (e.code === "Space" || e.code === "ArrowUp") {
                isJumpHolding = true;
            }
        });

        window.addEventListener("keyup", (e) => {
            if (e.code === "Space" || e.code === "ArrowUp") {
                isJumpHolding = false;
            }
        });

        canvas.addEventListener("mousedown", () => {
            isJumpHolding = true;
        });

        window.addEventListener("mouseup", () => {
            isJumpHolding = false;
        });

        // 지형 생성 (간격이 매우 넓은 계단 및 길쭉한 조형물)
        function spawnElements() {
            const rand = Math.random();

            if (rand < 0.5) {
                // 1. 점프해서 겨우 넘어가는 넓은 간격의 계단
                const stepWidth = 40;
                const stepGap = 85; // 캐릭터 속도(5) 대비 빠듯하게 닿는 넓은 간격
                const stepHeight = 22;
                const totalSteps = 3;

                for (let i = 0; i < totalSteps; i++) {
                    const stepX = canvas.width + (i * (stepWidth + stepGap));
                    const stepY = FLOOR_Y - ((i + 1) * stepHeight);

                    terrains.push({
                        type: 'stair',
                        x: stepX,
                        y: stepY,
                        width: stepWidth,
                        height: FLOOR_Y - stepY
                    });

                    // 넓은 계단 사이에 가시 배치
                    if (i < totalSteps - 1) {
                        obstacles.push({
                            type: 'spike',
                            x: stepX + stepWidth + (stepGap / 2) - 10,
                            y: FLOOR_Y - 22,
                            width: 20,
                            height: 22
                        });
                    }
                }

                // 마지막 계단 위 코인
                const lastX = canvas.width + ((totalSteps - 1) * (stepWidth + stepGap));
                coins.push({
                    x: lastX + stepWidth / 2,
                    y: FLOOR_Y - (totalSteps * stepHeight) - 20,
                    radius: 8,
                    collected: false
                });

            } else if (rand < 0.8) {
                // 2. 가로로 길쭉한 발판 조형물
                const longWidth = 150;
                const longHeight = 22;
                const longY = FLOOR_Y - 55;

                terrains.push({
                    type: 'structure',
                    x: canvas.width,
                    y: longY,
                    width: longWidth,
                    height: longHeight
                });

                // 조형물 위에 가시 또는 코인 배치
                if (Math.random() > 0.5) {
                    obstacles.push({
                        type: 'spike',
                        x: canvas.width + 65,
                        y: longY - 22,
                        width: 20,
                        height: 22
                    });
                } else {
                    coins.push({
                        x: canvas.width + 75,
                        y: longY - 20,
                        radius: 8,
                        collected: false
                    });
                }

            } else {
                // 3. 바닥 가시 장애물
                obstacles.push({
                    type: 'spike',
                    x: canvas.width,
                    y: FLOOR_Y - 26,
                    width: 22,
                    height: 26
                });
            }
        }

        function update() {
            if (!gameStarted || gameOver) return;

            // 버튼 홀드 점프 처리
            if (isJumpHolding && player.isGrounded) {
                player.vy = jumpForce;
                player.isGrounded = false;
            }

            // 중력 및 이동
            player.vy += gravity;
            player.y += player.vy;

            // 회전
            if (!player.isGrounded) {
                player.rotation += 0.12;
            } else {
                player.rotation = Math.round(player.rotation / (Math.PI / 2)) * (Math.PI / 2);
            }

            // 스폰 주기
            frameCount++;
            if (frameCount % 85 === 0) {
                spawnElements();
            }

            // 위치 이동
            for (let t of terrains) t.x -= gameSpeed;
            for (let obs of obstacles) obs.x -= gameSpeed;
            for (let coin of coins) coin.x -= gameSpeed;

            // --- 지형 충돌 처리 ---
            player.isGrounded = false;

            for (let t of terrains) {
                const pRight = player.x + player.width;
                const pLeft = player.x;
                const pBottom = player.y + player.height;
                const pTop = player.y;

                const tRight = t.x + t.width;
                const tLeft = t.x;
                const tTop = t.y;
                const tBottom = t.y + t.height;

                if (pRight > tLeft && pLeft < tRight) {
                    // 착지 판정
                    if (player.vy >= 0 && pBottom >= tTop && pBottom - player.vy <= tTop + 12) {
                        player.y = tTop - player.height;
                        player.vy = 0;
                        player.isGrounded = true;
                    } 
                    // 측면 충돌 판정
                    else if (pBottom > tTop + 8 && pTop < tBottom) {
                        if (pRight - gameSpeed <= tLeft) {
                            triggerGameOver();
                        }
                    }
                }
            }

            // 바닥 착지
            if (player.y + player.height >= FLOOR_Y) {
                player.y = FLOOR_Y - player.height;
                player.vy = 0;
                player.isGrounded = true;
            }

            // --- 가시 충돌 ---
            for (let obs of obstacles) {
                if (obs.type === 'spike') {
                    if (
                        player.x + player.width > obs.x + 4 &&
                        player.x < obs.x + obs.width - 4 &&
                        player.y + player.height > obs.y + 4 &&
                        player.y < obs.y + obs.height
                    ) {
                        triggerGameOver();
                    }
                }
            }

            // --- 코인 획득 ---
            for (let coin of coins) {
                if (!coin.collected) {
                    const dist = Math.hypot((player.x + player.width / 2) - coin.x, (player.y + player.height / 2) - coin.y);
                    if (dist < player.width / 2 + coin.radius) {
                        coin.collected = true;
                        score += 500;
                        coinsCollected++;
                    }
                }
            }

            // 화면 밖 요소 정리
            if (terrains.length > 0 && terrains[0].x + 300 < 0) terrains.shift();
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

            // 바닥
            ctx.fillStyle = "#222233";
            ctx.fillRect(0, FLOOR_Y, canvas.width, canvas.height - FLOOR_Y);
            ctx.strokeStyle = "#00ffff";
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.moveTo(0, FLOOR_Y);
            ctx.lineTo(canvas.width, FLOOR_Y);
            ctx.stroke();

            // 지형
            for (let t of terrains) {
                ctx.fillStyle = "#0088ff";
                ctx.fillRect(t.x, t.y, t.width, t.height);
                ctx.strokeStyle = "#00ffff";
                ctx.lineWidth = 2;
                ctx.strokeRect(t.x, t.y, t.width, t.height);
                ctx.fillStyle = "#ffffff";
                ctx.fillRect(t.x, t.y, t.width, 3);
            }

            // 가시
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
                }
            }

            // 코인
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

            // 플레이어
            ctx.save();
            ctx.translate(player.x + player.width / 2, player.y + player.height / 2);
            ctx.rotate(player.rotation);

            ctx.fillStyle = "#00ffcc";
            ctx.fillRect(-player.width / 2, -player.height / 2, player.width, player.height);
            ctx.strokeStyle = "#ffffff";
            ctx.lineWidth = 2;
            ctx.strokeRect(-player.width / 2, -player.height / 2, player.width, player.height);

            ctx.fillStyle = "#111";
            ctx.fillRect(-5, -5, 4, 4);
            ctx.fillRect(2, -5, 4, 4);

            ctx.restore();

            // 점수 UI
            ctx.fillStyle = "#ffffff";
            ctx.font = "16px sans-serif";
            ctx.textAlign = "left";
            ctx.fillText("SCORE: " + score, 15, 30);
            ctx.fillStyle = "#ffd700";
            ctx.fillText("🪙 COINS: " + coinsCollected, 160, 30);
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
            gameStarted = true;
            init();
            startBGM();
            loop();
        }

        function restartGame() {
            cancelAnimationFrame(animationFrameId);
            initAudio();
            if (audioCtx.state === "suspended") {
                audioCtx.resume();
            }
            init();
            startBGM();
            loop();
        }
    </script>
</body>
</html>
"""

# Streamlit HTML 컴포넌트 출력
components.html(game_code, height=380)
