import streamlit as st
import streamlit.components.v1 as components

st.title("📐 Geometry Dash (Rings & Pads Added)")

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
            border: 2px solid #333;
            background-color: #050508;
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
            <div class="sub-text">공중 점프링(공점) & 점프 발판 추가!</div>
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
    <div id="info"><b>조작법:</b> CUBE(점프 / 공점 근처에서 클릭 시 공중 점프) | WAVE(대각 이동)</div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");
        const startOverlay = document.getElementById("startOverlay");
        const gameOverOverlay = document.getElementById("gameOverOverlay");
        const finalScoreText = document.getElementById("finalScore");

        const FLOOR_Y = 270;
        const CEIL_Y = 10;

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
            const violinChords = [FREQS.A4, FREQS.G4, FREQS.F4, FREQS.E4];

            let step = 0;
            bgmInterval = setInterval(() => {
                if (!audioCtx || audioCtx.state === "suspended") return;
                const now = audioCtx.currentTime;
                playPiano(pianoMelody[step % pianoMelody.length], now, 0.2);
                if (step % 4 === 0) {
                    playViolin(violinChords[Math.floor(step / 4) % violinChords.length], now, 0.6);
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

        let gameStarted = false;
        let gameOver = false;
        let score = 0;
        const gameSpeed = 5;
        const gravity = 0.58;
        const jumpForce = -9.2;
        const padJumpForce = -12.0;
        const ringJumpForce = -10.5;
        const waveSpeedY = 6;

        let playerMode = 'cube';
        let player, obstacles, terrains, interactiveElements, portals, trail, frameCount, animationFrameId;
        let isHolding = false;
        let justPressed = false;

        const modeSequence = ['wave', 'cube'];
        let modeIndex = 0;

        function init() {
            gameOver = false;
            score = 0;
            frameCount = 0;
            playerMode = 'cube';
            modeIndex = 0;
            obstacles = [];
            terrains = [];
            interactiveElements = [];
            portals = [];
            trail = [];

            player = {
                x: 80,
                y: FLOOR_Y - 24,
                width: 24,
                height: 24,
                vy: 0,
                isGrounded: true,
                rotation: 0
            };

            gameOverOverlay.style.display = "none";
            startOverlay.style.display = "none";
        }

        window.addEventListener("keydown", (e) => {
            if (e.code === "Space" || e.code === "ArrowUp") {
                if (!isHolding) justPressed = true;
                isHolding = true;
            }
        });
        window.addEventListener("keyup", (e) => {
            if (e.code === "Space" || e.code === "ArrowUp") isHolding = false;
        });
        canvas.addEventListener("mousedown", () => {
            if (!isHolding) justPressed = true;
            isHolding = true;
        });
        window.addEventListener("mouseup", () => { isHolding = false; });

        function spawnElements() {
            // [포탈 스폰] 420프레임(약 7초) 주기
            if (frameCount > 0 && frameCount % 420 === 0) {
                const targetMode = modeSequence[modeIndex % modeSequence.length];
                modeIndex++;
                portals.push({
                    x: canvas.width,
                    y: 100,
                    width: 35,
                    height: 110,
                    targetMode: targetMode
                });
                return;
            }

            // 스폰 패턴 제어 (65프레임 주기)
            if (frameCount % 65 === 0) {
                if (playerMode === 'cube') {
                    const rand = Math.random();

                    if (rand < 0.3) {
                        // 가로 구조물 + 위쪽에 공점(Ring) 배치
                        terrains.push({
                            type: 'structure',
                            x: canvas.width,
                            y: FLOOR_Y - 55,
                            width: 130,
                            height: 20
                        });
                        interactiveElements.push({
                            type: 'ring',
                            x: canvas.width + 65,
                            y: FLOOR_Y - 105,
                            radius: 12,
                            used: false
                        });
                    } else if (rand < 0.55) {
                        // 지상 발판(Pad) + 가시 장애물 구조
                        interactiveElements.push({
                            type: 'pad',
                            x: canvas.width + 10,
                            y: FLOOR_Y - 6,
                            width: 28,
                            height: 6
                        });
                        const spikeW = 20;
                        for (let i = 0; i < 2; i++) {
                            obstacles.push({
                                type: 'spike',
                                x: canvas.width + 70 + (i * spikeW),
                                y: FLOOR_Y - 22,
                                width: spikeW,
                                height: 22
                            });
                        }
                    } else if (rand < 0.8) {
                        // 1~2개 가시
                        const count = Math.random() > 0.5 ? 1 : 2;
                        const spikeW = 20;
                        for (let i = 0; i < count; i++) {
                            obstacles.push({
                                type: 'spike',
                                x: canvas.width + (i * spikeW),
                                y: FLOOR_Y - 22,
                                width: spikeW,
                                height: 22
                            });
                        }
                    } else {
                        // 3연속 가시 + 앞쪽 공점(Ring)으로 점프 유도
                        interactiveElements.push({
                            type: 'ring',
                            x: canvas.width - 25,
                            y: FLOOR_Y - 65,
                            radius: 12,
                            used: false
                        });
                        const spikeW = 18;
                        for (let i = 0; i < 3; i++) {
                            obstacles.push({
                                type: 'spike',
                                x: canvas.width + (i * spikeW),
                                y: FLOOR_Y - 22,
                                width: spikeW,
                                height: 22
                            });
                        }
                    }
                } else if (playerMode === 'wave') {
                    // WAVE 모드: 공중 톱니바퀴
                    const minY = CEIL_Y + 40;
                    const maxY = FLOOR_Y - 40;
                    const randomY1 = minY + Math.random() * (maxY - minY - 40);

                    obstacles.push({
                        type: 'saw',
                        x: canvas.width,
                        y: randomY1,
                        radius: 20
                    });

                    if (Math.random() > 0.4) {
                        obstacles.push({
                            type: 'saw',
                            x: canvas.width + 120,
                            y: randomY1 > (CEIL_Y + FLOOR_Y) / 2 ? randomY1 - 50 : randomY1 + 50,
                            radius: 20
                        });
                    }
                }
            }
        }

        function update() {
            if (!gameStarted || gameOver) return;

            if (playerMode === 'cube') {
                // 일반 바닥 점프
                if (isHolding && player.isGrounded) {
                    player.vy = jumpForce;
                    player.isGrounded = false;
                }

                // 공중 점프링(Ring) 터치 상호작용
                if (justPressed) {
                    for (let el of interactiveElements) {
                        if (el.type === 'ring' && !el.used) {
                            const pCenterX = player.x + player.width / 2;
                            const pCenterY = player.y + player.height / 2;
                            const dist = Math.hypot(pCenterX - el.x, pCenterY - el.y);
                            if (dist < el.radius + 22) {
                                player.vy = ringJumpForce;
                                player.isGrounded = false;
                                el.used = true;
                                break;
                            }
                        }
                    }
                }

                player.vy += gravity;
                player.y += player.vy;

                if (!player.isGrounded) {
                    player.rotation += 0.12;
                } else {
                    player.rotation = Math.round(player.rotation / (Math.PI / 2)) * (Math.PI / 2);
                }
            } else if (playerMode === 'wave') {
                if (isHolding) {
                    player.y -= waveSpeedY;
                    player.rotation = -Math.PI / 4;
                } else {
                    player.y += waveSpeedY;
                    player.rotation = Math.PI / 4;
                }

                trail.push({ x: player.x + player.width / 2, y: player.y + player.height / 2 });
                if (trail.length > 25) trail.shift();

                if (player.y <= CEIL_Y || player.y + player.height >= FLOOR_Y) {
                    triggerGameOver();
                }
            }

            frameCount++;
            spawnElements();

            for (let t of terrains) t.x -= gameSpeed;
            for (let obs of obstacles) obs.x -= gameSpeed;
            for (let el of interactiveElements) el.x -= gameSpeed;
            for (let p of portals) p.x -= gameSpeed;
            for (let tr of trail) tr.x -= gameSpeed;

            // 포탈 충돌
            for (let p of portals) {
                if (
                    player.x + player.width > p.x &&
                    player.x < p.x + p.width &&
                    player.y + player.height > p.y &&
                    player.y < p.y + p.height
                ) {
                    if (playerMode !== p.targetMode) {
                        playerMode = p.targetMode;
                        player.vy = 0;
                        trail = [];
                    }
                }
            }

            // 지형 및 발판(Pad) 상호작용 Check
            if (playerMode === 'cube') {
                player.isGrounded = false;

                // 점프 발판(Pad) 접촉 판정
                for (let el of interactiveElements) {
                    if (el.type === 'pad') {
                        if (
                            player.x + player.width > el.x &&
                            player.x < el.x + el.width &&
                            player.y + player.height >= el.y &&
                            player.y + player.height <= el.y + el.height + 8
                        ) {
                            player.vy = padJumpForce;
                            player.isGrounded = false;
                        }
                    }
                }

                // 가로 구조물 지형
                for (let t of terrains) {
                    const pRight = player.x + player.width;
                    const pLeft = player.x;
                    const pBottom = player.y + player.height;
                    const pTop = player.y;

                    if (pRight > t.x && pLeft < t.x + t.width) {
                        if (player.vy >= 0 && pBottom >= t.y && pBottom - player.vy <= t.y + 12) {
                            player.y = t.y - player.height;
                            player.vy = 0;
                            player.isGrounded = true;
                        } else if (pBottom > t.y + 8 && pTop < t.y + t.height) {
                            if (pRight - gameSpeed <= t.x) triggerGameOver();
                        }
                    }
                }

                if (player.y + player.height >= FLOOR_Y) {
                    player.y = FLOOR_Y - player.height;
                    player.vy = 0;
                    player.isGrounded = true;
                }
            } else {
                for (let t of terrains) {
                    if (
                        player.x + player.width > t.x &&
                        player.x < t.x + t.width &&
                        player.y + player.height > t.y &&
                        player.y < t.y + t.height
                    ) {
                        triggerGameOver();
                    }
                }
            }

            // 장애물 충돌 (가시 & 톱니바퀴)
            for (let obs of obstacles) {
                if (obs.type === 'spike') {
                    if (
                        player.x + player.width - 4 > obs.x + 3 &&
                        player.x + 4 < obs.x + obs.width - 3 &&
                        player.y + player.height > obs.y + 4
                    ) {
                        triggerGameOver();
                    }
                } else if (obs.type === 'saw') {
                    const dist = Math.hypot((player.x + player.width / 2) - obs.x, (player.y + player.height / 2) - obs.y);
                    if (dist < player.width / 2 + obs.radius - 2) {
                        triggerGameOver();
                    }
                }
            }

            // 화면 밖 제거
            if (terrains.length > 0 && terrains[0].x + 300 < 0) terrains.shift();
            if (obstacles.length > 0 && obstacles[0].x + 100 < 0) obstacles.shift();
            if (interactiveElements.length > 0 && interactiveElements[0].x + 100 < 0) interactiveElements.shift();
            if (portals.length > 0 && portals[0].x + 100 < 0) portals.shift();

            if (!gameOver) score += Math.floor(gameSpeed / 3);
            justPressed = false;
        }

        function triggerGameOver() {
            gameOver = true;
            stopBGM();
            finalScoreText.innerText = "SCORE: " + score;
            gameOverOverlay.style.display = "flex";
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            if (!gameStarted) return;

            // 얇은 바닥 라인
            ctx.strokeStyle = "#334466";
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(0, FLOOR_Y);
            ctx.lineTo(canvas.width, FLOOR_Y);
            ctx.stroke();

            // Wave 잔상
            if (playerMode === 'wave' && trail.length > 1) {
                ctx.strokeStyle = "rgba(255, 0, 85, 0.6)";
                ctx.lineWidth = 4;
                ctx.beginPath();
                ctx.moveTo(trail[0].x, trail[0].y);
                for (let i = 1; i < trail.length; i++) ctx.lineTo(trail[i].x, tr.y);
                ctx.stroke();
            }

            // 포탈
            for (let p of portals) {
                ctx.fillStyle = p.targetMode === 'wave' ? "#ff00aa" : "#00ffff";
                ctx.fillRect(p.x, p.y, p.width, p.height);
                ctx.strokeStyle = "#ffffff";
                ctx.lineWidth = 3;
                ctx.strokeRect(p.x, p.y, p.width, p.height);

                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 11px sans-serif";
                ctx.textAlign = "center";
                ctx.fillText(p.targetMode.toUpperCase(), p.x + p.width / 2, p.y + p.height / 2);
            }

            // 구조물 지형
            for (let t of terrains) {
                ctx.fillStyle = "#0088ff";
                ctx.fillRect(t.x, t.y, t.width, t.height);
                ctx.strokeStyle = "#ffffff";
                ctx.lineWidth = 1.5;
                ctx.strokeRect(t.x, t.y, t.width, t.height);
            }

            // 공점(Ring) 및 점프 발판(Pad)
            for (let el of interactiveElements) {
                if (el.type === 'ring') {
                    ctx.strokeStyle = el.used ? "#888888" : "#ffe600";
                    ctx.lineWidth = 3;
                    ctx.beginPath();
                    ctx.arc(el.x, el.y, el.radius, 0, Math.PI * 2);
                    ctx.stroke();

                    // 내부에 미세한 점 표시
                    ctx.fillStyle = el.used ? "#555555" : "#ffffff";
                    ctx.beginPath();
                    ctx.arc(el.x, el.y, 4, 0, Math.PI * 2);
                    ctx.fill();
                } else if (el.type === 'pad') {
                    ctx.fillStyle = "#ffe600";
                    ctx.fillRect(el.x, el.y, el.width, el.height);
                    ctx.strokeStyle = "#ffffff";
                    ctx.lineWidth = 1;
                    ctx.strokeRect(el.x, el.y, el.width, el.height);
                }
            }

            // 장애물 (가시 & 톱니바퀴)
            for (let obs of obstacles) {
                if (obs.type === 'spike') {
                    ctx.fillStyle = "#ff3300";
                    ctx.beginPath();
                    ctx.moveTo(obs.x, obs.y + obs.height);
                    ctx.lineTo(obs.x + obs.width / 2, obs.y);
                    ctx.lineTo(obs.x + obs.width, obs.y + obs.height);
                    ctx.closePath();
                    ctx.fill();
                    ctx.strokeStyle = "#ffffff";
                    ctx.lineWidth = 1;
                    ctx.stroke();
                } else if (obs.type === 'saw') {
                    ctx.fillStyle = "#ff3300";
                    ctx.beginPath();
                    ctx.arc(obs.x, obs.y, obs.radius, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.strokeStyle = "#ffffff";
                    ctx.lineWidth = 2;
                    ctx.stroke();
                }
            }

            // 플레이어
            ctx.save();
            ctx.translate(player.x + player.width / 2, player.y + player.height / 2);
            ctx.rotate(player.rotation);

            if (playerMode === 'cube') {
                ctx.fillStyle = "#00ffcc";
                ctx.fillRect(-player.width / 2, -player.height / 2, player.width, player.height);
                ctx.strokeStyle = "#ffffff";
                ctx.lineWidth = 2;
                ctx.strokeRect(-player.width / 2, -player.height / 2, player.width, player.height);
            } else if (playerMode === 'wave') {
                ctx.fillStyle = "#ff0055";
                ctx.beginPath();
                ctx.moveTo(14, 0);
                ctx.lineTo(-10, -10);
                ctx.lineTo(-4, 0);
                ctx.lineTo(-10, 10);
                ctx.closePath();
                ctx.fill();
                ctx.strokeStyle = "#ffffff";
                ctx.lineWidth = 1.5;
                ctx.stroke();
            }
            ctx.restore();

            // 점수 및 현재 모드 UI
            ctx.fillStyle = "#ffffff";
            ctx.font = "16px sans-serif";
            ctx.textAlign = "left";
            ctx.fillText("SCORE: " + score, 15, 25);
            ctx.fillStyle = playerMode === 'wave' ? "#ff0055" : "#00ffcc";
            ctx.fillText("MODE: " + playerMode.toUpperCase(), 150, 25);
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
            if (audioCtx.state === "suspended") audioCtx.resume();
            gameStarted = true;
            init();
            startBGM();
            loop();
        }

        function restartGame() {
            cancelAnimationFrame(animationFrameId);
            initAudio();
            if (audioCtx.state === "suspended") audioCtx.resume();
            init();
            startBGM();
            loop();
        }
    </script>
</body>
</html>
"""

components.html(game_code, height=380)
