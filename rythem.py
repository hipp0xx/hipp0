import streamlit as st
import streamlit.components.v1 as components

st.title("📐 Geometry Dash (Custom Obstacles & Thin Floor)")

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
            <div class="sub-text">7초 포탈 & 3연속 가시 등장!</div>
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
    <div id="info"><b>조작법:</b> CUBE(연속 점프) | WAVE(직선 대각 이동) | SHIP(추진력 상승 & 브레스 연출)</div>

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
        const waveSpeedY = 6;

        let playerMode = 'cube';
        let player, obstacles, terrains, portals, trail, flames, frameCount, animationFrameId;
        let isHolding = false;

        const modeSequence = ['wave', 'ship', 'cube'];
        let modeIndex = 0;

        function init() {
            gameOver = false;
            score = 0;
            frameCount = 0;
            playerMode = 'cube';
            modeIndex = 0;
            obstacles = [];
            terrains = [];
            portals = [];
            trail = [];
            flames = [];

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
            if (e.code === "Space" || e.code === "ArrowUp") isHolding = true;
        });
        window.addEventListener("keyup", (e) => {
            if (e.code === "Space" || e.code === "ArrowUp") isHolding = false;
        });
        canvas.addEventListener("mousedown", () => { isHolding = true; });
        window.addEventListener("mouseup", () => { isHolding = false; });

        function spawnElements() {
            // [포탈 스폰] 420프레임(약 7초) 주기 스폰
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

            // 장애물 및 지형 스폰 (65프레임 주기)
            if (frameCount % 65 === 0) {
                if (playerMode === 'cube') {
                    const rand = Math.random();

                    if (rand < 0.4) {
                        // 가로 구조물
                        terrains.push({
                            type: 'structure',
                            x: canvas.width,
                            y: FLOOR_Y - 50,
                            width: 140,
                            height: 20
                        });
                    } else if (rand < 0.85) {
                        // 1개 또는 2개 가시
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
                        // 아주 가끔 나오는 3개짜리 가시 (넘을 수 있는 타이밍 배치)
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
                    // 공중 톱니바퀴
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
                } else if (playerMode === 'ship') {
                    // 비행선 전용 기둥 장애물
                    terrains.push({
                        type: 'pillar',
                        x: canvas.width,
                        y: 0,
                        width: 40,
                        height: 80
                    });
                    terrains.push({
                        type: 'pillar',
                        x: canvas.width,
                        y: FLOOR_Y - 80,
                        width: 40,
                        height: 80
                    });
                }
            }
        }

        function update() {
            if (!gameStarted || gameOver) return;

            if (playerMode === 'cube') {
                if (isHolding && player.isGrounded) {
                    player.vy = jumpForce;
                    player.isGrounded = false;
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
            } else if (playerMode === 'ship') {
                if (isHolding) {
                    player.vy -= 0.45;
                    flames.push({
                        x: player.x - 10,
                        y: player.y + player.height / 2 + (Math.random() * 6 - 3),
                        vx: - (Math.random() * 3 + 4),
                        vy: Math.random() * 2 - 1,
                        size: Math.random() * 6 + 4,
                        life: 1.0
                    });
                } else {
                    player.vy += 0.35;
                }
                player.vy = Math.max(-6, Math.min(6, player.vy));
                player.y += player.vy;
                player.rotation = player.vy * 0.08;

                if (player.y <= CEIL_Y || player.y + player.height >= FLOOR_Y) {
                    triggerGameOver();
                }
            }

            // 브레스 파티클 업데이트
            for (let i = flames.length - 1; i >= 0; i--) {
                const f = flames[i];
                f.x += f.vx;
                f.y += f.vy;
                f.life -= 0.05;
                if (f.life <= 0) flames.splice(i, 1);
            }

            frameCount++;
            spawnElements();

            for (let t of terrains) t.x -= gameSpeed;
            for (let obs of obstacles) obs.x -= gameSpeed;
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

            // 지형 충돌
            if (playerMode === 'cube') {
                player.isGrounded = false;
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
                    // 히트박스를 살짝 여유있게 조정하여 3연속 가시 점프가 가능하도록 함
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

            if (terrains.length > 0 && terrains[0].x + 300 < 0) terrains.shift();
            if (obstacles.length > 0 && obstacles[0].x + 100 < 0) obstacles.shift();
            if (portals.length > 0 && portals[0].x + 100 < 0) portals.shift();

            if (!gameOver) score += Math.floor(gameSpeed / 3);
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
                for (let i = 1; i < trail.length; i++) ctx.lineTo(trail[i].x, trail[i].y);
                ctx.stroke();
            }

            // 비행선 브레스 파티클
            for (let f of flames) {
                ctx.fillStyle = `rgba(255, ${Math.floor(f.life * 200)}, 0, ${f.life})`;
                ctx.beginPath();
                ctx.arc(f.x, f.y, f.size * f.life, 0, Math.PI * 2);
                ctx.fill();
            }

            // 포탈
            for (let p of portals) {
                ctx.fillStyle = p.targetMode === 'wave' ? "#ff00aa" : (p.targetMode === 'ship' ? "#00ff66" : "#00ffff");
                ctx.fillRect(p.x, p.y, p.width, p.height);
                ctx.strokeStyle = "#ffffff";
                ctx.lineWidth = 3;
                ctx.strokeRect(p.x, p.y, p.width, p.height);

                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 11px sans-serif";
                ctx.textAlign = "center";
                ctx.fillText(p.targetMode.toUpperCase(), p.x + p.width / 2, p.y + p.height / 2);
            }

            // 지형 (가로 구조물)
            for (let t of terrains) {
                ctx.fillStyle = "#0088ff";
                ctx.fillRect(t.x, t.y, t.width, t.height);
                ctx.strokeStyle = "#ffffff";
                ctx.lineWidth = 1.5;
                ctx.strokeRect(t.x, t.y, t.width, t.height);
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
            } else if (playerMode === 'ship') {
                ctx.fillStyle = "#00ff66";
                ctx.beginPath();
                ctx.ellipse(0, 0, 14, 8, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.strokeStyle = "#ffffff";
                ctx.lineWidth = 2;
                ctx.stroke();
            }
            ctx.restore();

            // UI
            ctx.fillStyle = "#ffffff";
            ctx.font = "16px sans-serif";
            ctx.textAlign = "left";
            ctx.fillText("SCORE: " + score, 15, 25);
            ctx.fillStyle = playerMode === 'wave' ? "#ff0055" : (playerMode === 'ship' ? "#00ff66" : "#00ffcc");
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
