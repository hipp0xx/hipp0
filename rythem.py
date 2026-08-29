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

        // Web Audio API 설정 (피아노 + 바이올린 + 베이스 합성)
        let audioCtx = null;
        let bgmInterval = null;

        function initAudio() {
            if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            }
        }

        // 음고(Hz) 변환 표 (Am 키 기반)
        const FREQS = {
            A2: 110.00, C3: 130.81, E3: 164.81, G3: 196.00,
            A3: 220.00, C4: 261.63, E4: 329.63, F4: 349.23,
            G4: 392.00, A4: 440.00, B4: 493.88, C5: 523.25, E5: 659.25
        };

        // 피아노음 생성 (부드럽고 빠른 감쇄)
        function playPiano(freq, time, duration = 0.25) {
            if (!audioCtx) return;
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();

            osc.type = "triangle"; // 피아노 톤에 가까운 삼각파
            osc.frequency.setValueAtTime(freq, time);

            gain.gain.setValueAtTime(0.15, time);
            gain.gain.exponentialRampToValueAtTime(0.001, time + duration);

            osc.connect(gain);
            gain.connect(audioCtx.destination);

            osc.start(time);
            osc.stop(time + duration);
        }

        // 바이올린/스트링음 생성 (바이브라토 + 풍성한 배음)
        function playViolin(freq, time, duration = 0.5) {
            if (!audioCtx) return;
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            const lfo = audioCtx.createOscillator(); // 바이브라토 연출용
            const lfoGain = audioCtx.createGain();

            osc.type = "sawtooth";
            osc.frequency.setValueAtTime(freq, time);

            // 바이브라토 (떨림) 설정
            lfo.frequency.setValueAtTime(6, time); // 6Hz 떨림
            lfoGain.gain.setValueAtTime(3, time); // 떨림 폭
            lfo.connect(osc.frequency);

            // 서서히 커졌다가 감싸안듯 줄어드는 볼륨 커브
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

        // 지오메트리 대쉬 스타일 BGM 시퀀서
        function startBGM() {
            if (!audioCtx) return;
            stopBGM();

            // 빠른 피아노 메인 리프 패턴
            const pianoMelody = [
                FREQS.A4, FREQS.C5, FREQS.E5, FREQS.C5,
                FREQS.G4, FREQS.B4, FREQS.E5, FREQS.B4,
                FREQS.F4, FREQS.A4, FREQS.C5, FREQS.A4,
                FREQS.E4, FREQS.G4, FREQS.B4, FREQS.G4
            ];

            // 웅장하게 받쳐주는 바이올린 화음 패턴
            const violinChords = [
                FREQS.A4, FREQS.G4, FREQS.F4, FREQS.E4
            ];

            let step = 0;

            bgmInterval = setInterval(() => {
                if (!audioCtx || audioCtx.state === "suspended") return;

                const now = audioCtx.currentTime;

                // 1. 빠른 피아노 멜로디 (매 비트마다)
                const pFreq = pianoMelody[step % pianoMelody.length];
                playPiano(pFreq, now, 0.2);

                // 2. 4비트마다 배경을 채워주는 바이올린 롱톤
                if (step % 4 === 0) {
                    const vFreq = violinChords[Math.floor(step / 4) % violinChords.length];
                    playViolin(vFreq, now, 0.6);
                }

                step++;
            }, 120); // 125 BPM
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

        // 게임 초기화
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

        function spawnElements() {
            const rand = Math.random();

            if (rand < 0.25) {
                const isFast = gameSpeed <= 5;
                portals.push({
                    x: canvas.width,
                    y: Math.random() * (canvas.height - 100) + 50,
                    width: 20,
                    height: 60,
                    type: isFast ? 'fast' : 'slow',
                    active: true
                });
            } else if (rand < 0.6) {
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
            if (!gameStarted || gameOver) return;

            const currentSpeedY = player.speedY * (gameSpeed / 5);
            if (isPressing) {
                player.y -= currentSpeedY;
            } else {
                player.y += currentSpeedY;
            }

            trail.push({ x: player.x, y: player.y });
            for (let i = 0; i < trail.length; i++) {
                trail[i].x -= gameSpeed;
            }
            while (trail.length > 0 && trail[0].x < 0) {
                trail.shift();
            }

            if (player.y - player.size < 0 || player.y + player.size > canvas.height) {
                triggerGameOver();
            }

            frameCount++;
            if (frameCount % 45 === 0) {
                spawnElements();
            }

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

            if (obstacles.length > 0 && obstacles[0].x + obstacles[0].width < 0) obstacles.shift();
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

            // 1. 잔상
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

            // 3. 장애물
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

            // 5. 플레이어
            ctx.fillStyle = gameSpeed > 5 ? "#ffcc00" : "#00ffff";
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
