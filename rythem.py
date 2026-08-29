<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Geometry Dash Web - Wave Fix & Enhanced Pads</title>
    <style>
        * {
            box-sizing: border-box;
            user-select: none;
            -webkit-user-select: none;
            margin: 0;
            padding: 0;
        }

        body {
            background-color: #0b0c10;
            color: #ffffff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            overflow: hidden;
        }

        #game-container {
            position: relative;
            width: 960px;
            height: 540px;
            background: #000;
            border-radius: 12px;
            box-shadow: 0 0 30px rgba(0, 240, 255, 0.3), 0 0 10px rgba(0, 0, 0, 0.8);
            overflow: hidden;
        }

        canvas {
            display: block;
            width: 100%;
            height: 100%;
        }

        /* HUD Overlay */
        #hud {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 16px;
        }

        .top-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
        }

        .progress-container {
            flex-grow: 1;
            max-width: 400px;
            height: 16px;
            background: rgba(255, 255, 255, 0.15);
            border-radius: 8px;
            overflow: hidden;
            border: 2px solid rgba(255, 255, 255, 0.3);
            margin: 0 20px;
            position: relative;
        }

        .progress-bar {
            height: 100%;
            width: 0%;
            background: linear-gradient(90deg, #00f0ff, #7000ff);
            box-shadow: 0 0 10px #00f0ff;
            transition: width 0.1s linear;
        }

        .stats-text {
            font-size: 18px;
            font-weight: 800;
            text-shadow: 0 0 6px rgba(0, 240, 255, 0.8), 2px 2px 4px #000;
            letter-spacing: 1px;
        }

        .mode-badge {
            background: rgba(0, 0, 0, 0.6);
            border: 2px solid #00f0ff;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
            color: #00f0ff;
            text-transform: uppercase;
            box-shadow: 0 0 10px rgba(0, 240, 255, 0.4);
        }

        /* Menu Overlay */
        .overlay-screen {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(10, 10, 20, 0.85);
            backdrop-filter: blur(8px);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 10;
            pointer-events: auto;
        }

        h1 {
            font-size: 48px;
            font-weight: 900;
            background: linear-gradient(45deg, #00f0ff, #ff007f, #ffe600);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
            text-shadow: 0 0 20px rgba(0, 240, 255, 0.5);
            letter-spacing: 2px;
        }

        .sub-title {
            color: #a0a0c0;
            font-size: 16px;
            margin-bottom: 30px;
        }

        .btn-group {
            display: flex;
            gap: 16px;
        }

        .btn {
            background: linear-gradient(135deg, #00f0ff, #0072ff);
            color: #fff;
            border: none;
            padding: 14px 32px;
            font-size: 18px;
            font-weight: bold;
            border-radius: 30px;
            cursor: pointer;
            box-shadow: 0 0 15px rgba(0, 240, 255, 0.5);
            transition: all 0.2s ease;
        }

        .btn:hover {
            transform: translateY(-3px) scale(1.05);
            box-shadow: 0 0 25px rgba(0, 240, 255, 0.8);
        }

        .btn-secondary {
            background: linear-gradient(135deg, #ff007f, #7000ff);
            box-shadow: 0 0 15px rgba(255, 0, 127, 0.5);
        }

        .btn-secondary:hover {
            box-shadow: 0 0 25px rgba(255, 0, 127, 0.8);
        }

        .controls-hint {
            position: absolute;
            bottom: 20px;
            color: #888;
            font-size: 14px;
            text-align: center;
            line-height: 1.6;
        }

        .key {
            background: #222;
            border: 1px solid #555;
            padding: 2px 8px;
            border-radius: 4px;
            color: #fff;
            font-weight: bold;
        }

        /* Practice Mode Controls */
        .practice-controls {
            position: absolute;
            bottom: 16px;
            left: 16px;
            display: flex;
            gap: 10px;
            pointer-events: auto;
        }

        .btn-small {
            background: rgba(0, 0, 0, 0.7);
            border: 1px solid #00f0ff;
            color: #fff;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: bold;
            cursor: pointer;
        }

        .btn-small:hover {
            background: #00f0ff;
            color: #000;
        }
    </style>
</head>
<body>

    <div id="game-container">
        <canvas id="gameCanvas" width="960" height="540"></canvas>

        <!-- HUD -->
        <div id="hud">
            <div class="top-bar">
                <div class="stats-text" id="attemptText">시도: 1</div>
                <div class="progress-container">
                    <div class="progress-bar" id="progressBar"></div>
                </div>
                <div class="stats-text" id="percentText">0%</div>
                <div class="mode-badge" id="modeBadge">CUBE</div>
            </div>

            <div class="practice-controls" id="practiceControls" style="display: none;">
                <button class="btn-small" id="btnCheckpoint">+ 체크포인트 (Z)</button>
                <button class="btn-small" id="btnRemoveCheckpoint">- 삭제 (X)</button>
            </div>
        </div>

        <!-- Start Overlay -->
        <div class="overlay-screen" id="startScreen">
            <h1>GEOMETRY DASH</h1>
            <p class="sub-title">웨이브 모드 수정 & 개선된 점프발판 버전</p>
            <div class="btn-group">
                <button class="btn" id="btnPlay">일반 모드 시작</button>
                <button class="btn btn-secondary" id="btnPractice">연습 모드</button>
            </div>
            <div class="controls-hint">
                점프 / 비행 / 웨이브 조작: <span class="key">Space</span> / <span class="key">마우스 클릭</span> / <span class="key">↑ 화살표</span><br>
                연습모드 체크포인트: <span class="key">Z</span> 생성 | <span class="key">X</span> 삭제 | 일시정지: <span class="key">P</span> / <span class="key">Esc</span>
            </div>
        </div>

        <!-- Death/Game Over Screen -->
        <div class="overlay-screen" id="deathScreen" style="display: none;">
            <h1 style="background: linear-gradient(45deg, #ff0055, #ff5500); -webkit-background-clip: text;">CRASHED!</h1>
            <p class="sub-title" id="deathMessage">진행도: 0%</p>
            <div class="btn-group">
                <button class="btn" id="btnRestart">다시 시도</button>
            </div>
        </div>
    </div>

    <script>
        // --- Web Audio API Synthesizer Sound Generator ---
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        let audioCtx = null;

        function initAudio() {
            if (!audioCtx) {
                audioCtx = new AudioCtx();
            }
            if (audioCtx.state === 'suspended') {
                audioCtx.resume();
            }
        }

        function playSound(type) {
            if (!audioCtx) return;
            const now = audioCtx.currentTime;
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.connect(gain);
            gain.connect(audioCtx.destination);

            if (type === 'jump') {
                osc.type = 'sine';
                osc.frequency.setValueAtTime(150, now);
                osc.frequency.exponentialRampToValueAtTime(400, now + 0.12);
                gain.gain.setValueAtTime(0.3, now);
                gain.gain.linearRampToValueAtTime(0.01, now + 0.12);
                osc.start(now);
                osc.stop(now + 0.12);
            } else if (type === 'pad') {
                osc.type = 'triangle';
                osc.frequency.setValueAtTime(200, now);
                osc.frequency.exponentialRampToValueAtTime(700, now + 0.2);
                gain.gain.setValueAtTime(0.5, now);
                gain.gain.linearRampToValueAtTime(0.01, now + 0.2);
                osc.start(now);
                osc.stop(now + 0.2);
            } else if (type === 'portal') {
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(300, now);
                osc.frequency.linearRampToValueAtTime(600, now + 0.15);
                gain.gain.setValueAtTime(0.2, now);
                gain.gain.linearRampToValueAtTime(0.01, now + 0.15);
                osc.start(now);
                osc.stop(now + 0.15);
            } else if (type === 'explode') {
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(120, now);
                osc.frequency.exponentialRampToValueAtTime(30, now + 0.3);
                gain.gain.setValueAtTime(0.6, now);
                gain.gain.linearRampToValueAtTime(0.01, now + 0.3);
                osc.start(now);
                osc.stop(now + 0.3);
            }
        }

        // --- Game Setup ---
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');

        // UI Elements
        const startScreen = document.getElementById('startScreen');
        const deathScreen = document.getElementById('deathScreen');
        const deathMessage = document.getElementById('deathMessage');
        const btnPlay = document.getElementById('btnPlay');
        const btnPractice = document.getElementById('btnPractice');
        const btnRestart = document.getElementById('btnRestart');
        const attemptText = document.getElementById('attemptText');
        const progressBar = document.getElementById('progressBar');
        const percentText = document.getElementById('percentText');
        const modeBadge = document.getElementById('modeBadge');
        const practiceControls = document.getElementById('practiceControls');
        const btnCheckpoint = document.getElementById('btnCheckpoint');
        const btnRemoveCheckpoint = document.getElementById('btnRemoveCheckpoint');

        // Constants & Configs
        const GRAVITY = 0.85;
        const JUMP_FORCE = -13.5;
        const CUBE_SPEED = 7.5;
        const FLOOR_Y = 440;
        const CEILING_Y = 60;
        const PLAYER_SIZE = 36;

        // Enlarged Spike Configs
        const SPIKE_WIDTH = 42;  // Increased size
        const SPIKE_HEIGHT = 44; // Increased size

        // Game State Variables
        let gameState = 'START'; // 'START', 'PLAYING', 'DEAD', 'PAUSED'
        let isPracticeMode = false;
        let attempts = 1;
        let cameraX = 0;
        let isHoldingInput = false;

        // Player State
        let player = {
            x: 100,
            y: FLOOR_Y - PLAYER_SIZE,
            vx: CUBE_SPEED,
            vy: 0,
            rotation: 0,
            mode: 'CUBE', // 'CUBE', 'SHIP', 'WAVE'
            isGrounded: false,
            gravityDir: 1, // 1 normal, -1 inverted
            waveTrail: []  // Fix: Safe Wave Trail array
        };

        // Particles
        let particles = [];
        let checkpoints = [];

        // --- Level Generation ---
        // Types: 'block', 'spike', 'pad_yellow', 'pad_blue', 'portal_ship', 'portal_wave', 'portal_cube'
        let levelObjects = [];
        const LEVEL_LENGTH = 12000;

        function generateLevel() {
            levelObjects = [];
            let x = 600;

            // Section 1: Cube Basics & Big Spikes
            while (x < 2800) {
                // Spikes
                if (Math.random() < 0.4) {
                    levelObjects.push({ type: 'spike', x: x, y: FLOOR_Y - SPIKE_HEIGHT, w: SPIKE_WIDTH, h: SPIKE_HEIGHT });
                    if (Math.random() < 0.3) {
                        levelObjects.push({ type: 'spike', x: x + SPIKE_WIDTH, y: FLOOR_Y - SPIKE_HEIGHT, w: SPIKE_WIDTH, h: SPIKE_HEIGHT });
                    }
                    x += 180;
                } 
                // Blocks with Jump Pads
                else if (Math.random() < 0.4) {
                    let blockH = 50 + Math.floor(Math.random() * 2) * 40;
                    levelObjects.push({ type: 'block', x: x, y: FLOOR_Y - blockH, w: 120, h: blockH });

                    if (Math.random() < 0.5) {
                        // Improved Pad on block
                        levelObjects.push({ type: 'pad_yellow', x: x + 40, y: FLOOR_Y - blockH - 14, w: 40, h: 14 });
                    }
                    x += 220;
                } else {
                    // Ground pad
                    levelObjects.push({ type: 'pad_yellow', x: x, y: FLOOR_Y - 14, w: 44, h: 14 });
                    x += 200;
                }
            }

            // Portal to SHIP Mode
            levelObjects.push({ type: 'portal_ship', x: 2900, y: FLOOR_Y - 160, w: 40, h: 90 });

            // Section 2: Ship Mode (Obstacles in mid-air)
            x = 3200;
            while (x < 5500) {
                let wallHeight = 100 + Math.random() * 140;
                let isTop = Math.random() < 0.5;

                if (isTop) {
                    levelObjects.push({ type: 'block', x: x, y: CEILING_Y, w: 80, h: wallHeight });
                    levelObjects.push({ type: 'spike_down', x: x + 18, y: CEILING_Y + wallHeight, w: SPIKE_WIDTH, h: SPIKE_HEIGHT });
                } else {
                    levelObjects.push({ type: 'block', x: x, y: FLOOR_Y - wallHeight, w: 80, h: wallHeight });
                    levelObjects.push({ type: 'spike', x: x + 18, y: FLOOR_Y - wallHeight - SPIKE_HEIGHT, w: SPIKE_WIDTH, h: SPIKE_HEIGHT });
                }

                x += 260;
            }

            // Portal to WAVE Mode
            levelObjects.push({ type: 'portal_wave', x: 5700, y: FLOOR_Y - 160, w: 40, h: 90 });

            // Section 3: Wave Mode Slaloms
            x = 6000;
            while (x < 9000) {
                // Top hazard
                let topH = 80 + Math.random() * 100;
                let botH = 80 + Math.random() * 100;

                levelObjects.push({ type: 'block', x: x, y: CEILING_Y, w: 100, h: topH });
                levelObjects.push({ type: 'block', x: x, y: FLOOR_Y - botH, w: 100, h: botH });

                x += 300;
            }

            // Portal back to CUBE Mode
            levelObjects.push({ type: 'portal_cube', x: 9300, y: FLOOR_Y - 160, w: 40, h: 90 });

            // Final Dash
            x = 9600;
            while (x < LEVEL_LENGTH - 400) {
                levelObjects.push({ type: 'spike', x: x, y: FLOOR_Y - SPIKE_HEIGHT, w: SPIKE_WIDTH, h: SPIKE_HEIGHT });
                if (Math.random() < 0.5) {
                    levelObjects.push({ type: 'pad_yellow', x: x - 60, y: FLOOR_Y - 14, w: 44, h: 14 });
                }
                x += 280;
            }
        }

        // --- Reset Game ---
        function resetGame(fullReset = true) {
            if (fullReset) {
                player.x = 100;
                player.y = FLOOR_Y - PLAYER_SIZE;
                player.vx = CUBE_SPEED;
                player.vy = 0;
                player.rotation = 0;
                player.mode = 'CUBE';
                player.gravityDir = 1;
                player.waveTrail = [];
                cameraX = 0;
            } else if (checkpoints.length > 0) {
                // Practice checkpoint restore
                const cp = checkpoints[checkpoints.length - 1];
                player.x = cp.x;
                player.y = cp.y;
                player.mode = cp.mode;
                player.gravityDir = cp.gravityDir;
                player.vx = CUBE_SPEED;
                player.vy = 0;
                player.rotation = 0;
                player.waveTrail = [];
                cameraX = player.x - 150;
            }
            particles = [];
            modeBadge.innerText = player.mode;
            modeBadge.style.borderColor = player.mode === 'WAVE' ? '#ff007f' : (player.mode === 'SHIP' ? '#ffe600' : '#00f0ff');
            modeBadge.style.color = modeBadge.style.borderColor;
        }

        // --- Controls & Listeners ---
        function handleInputStart(e) {
            if (e.type === 'keydown' && e.code !== 'Space' && e.code !== 'ArrowUp' && e.code !== 'KeyZ' && e.code !== 'KeyX') return;
            initAudio();

            if (e.code === 'KeyZ' && isPracticeMode && gameState === 'PLAYING') {
                checkpoints.push({
                    x: player.x,
                    y: player.y,
                    mode: player.mode,
                    gravityDir: player.gravityDir
                });
                playSound('portal');
                return;
            }

            if (e.code === 'KeyX' && isPracticeMode && gameState === 'PLAYING') {
                if (checkpoints.length > 0) checkpoints.pop();
                return;
            }

            isHoldingInput = true;

            if (gameState === 'PLAYING') {
                if (player.mode === 'CUBE' && player.isGrounded) {
                    player.vy = JUMP_FORCE * player.gravityDir;
                    player.isGrounded = false;
                    playSound('jump');
                    createParticles(player.x + PLAYER_SIZE/2, player.y + PLAYER_SIZE, 8, '#00f0ff');
                }
            }
        }

        function handleInputEnd(e) {
            if (e.type === 'keyup' && e.code !== 'Space' && e.code !== 'ArrowUp') return;
            isHoldingInput = false;
        }

        window.addEventListener('keydown', handleInputStart);
        window.addEventListener('keyup', handleInputEnd);
        canvas.addEventListener('mousedown', (e) => { handleInputStart(e); });
        window.addEventListener('mouseup', handleInputEnd);
        canvas.addEventListener('touchstart', (e) => { e.preventDefault(); handleInputStart(e); }, { passive: false });
        window.addEventListener('touchend', handleInputEnd);

        btnPlay.addEventListener('click', () => {
            initAudio();
            isPracticeMode = false;
            practiceControls.style.display = 'none';
            attempts = 1;
            attemptText.innerText = `시도: ${attempts}`;
            startScreen.style.display = 'none';
            deathScreen.style.display = 'none';
            resetGame(true);
            gameState = 'PLAYING';
        });

        btnPractice.addEventListener('click', () => {
            initAudio();
            isPracticeMode = true;
            practiceControls.style.display = 'flex';
            checkpoints = [];
            attempts = 1;
            attemptText.innerText = `연습 시도: ${attempts}`;
            startScreen.style.display = 'none';
            deathScreen.style.display = 'none';
            resetGame(true);
            gameState = 'PLAYING';
        });

        btnRestart.addEventListener('click', () => {
            initAudio();
            deathScreen.style.display = 'none';
            if (!isPracticeMode) {
                attempts++;
                attemptText.innerText = `시도: ${attempts}`;
                resetGame(true);
            } else {
                resetGame(checkpoints.length === 0);
            }
            gameState = 'PLAYING';
        });

        btnCheckpoint.addEventListener('click', () => {
            if (isPracticeMode && gameState === 'PLAYING') {
                checkpoints.push({
                    x: player.x,
                    y: player.y,
                    mode: player.mode,
                    gravityDir: player.gravityDir
                });
                playSound('portal');
            }
        });

        btnRemoveCheckpoint.addEventListener('click', () => {
            if (checkpoints.length > 0) checkpoints.pop();
        });

        // --- Particle System ---
        function createParticles(x, y, count, color) {
            for (let i = 0; i < count; i++) {
                particles.push({
                    x: x,
                    y: y,
                    vx: (Math.random() - 0.5) * 8,
                    vy: (Math.random() - 0.5) * 8,
                    size: Math.random() * 6 + 3,
                    color: color,
                    life: 1.0
                });
            }
        }

        function updateParticles() {
            for (let i = particles.length - 1; i >= 0; i--) {
                let p = particles[i];
                p.x += p.vx;
                p.y += p.vy;
                p.life -= 0.04;
                if (p.life <= 0) {
                    particles.splice(i, 1);
                }
            }
        }

        function drawParticles() {
            particles.forEach(p => {
                ctx.save();
                ctx.globalAlpha = Math.max(0, p.life);
                ctx.fillStyle = p.color;
                ctx.fillRect(p.x - cameraX, p.y, p.size, p.size);
                ctx.restore();
            });
        }

        // --- Crash / Player Death ---
        function die() {
            if (gameState !== 'PLAYING') return;
            playSound('explode');
            createParticles(player.x + PLAYER_SIZE/2, player.y + PLAYER_SIZE/2, 25, '#ff0055');
            createParticles(player.x + PLAYER_SIZE/2, player.y + PLAYER_SIZE/2, 15, '#ffe600');
            gameState = 'DEAD';

            let currentPercent = Math.min(100, Math.floor((player.x / LEVEL_LENGTH) * 100));

            setTimeout(() => {
                deathMessage.innerText = `진행도: ${currentPercent}%`;
                deathScreen.style.display = 'flex';
            }, 400);
        }

        // --- Physics & Game Loop ---
        function update() {
            if (gameState !== 'PLAYING') return;

            // X movement
            player.x += player.vx;

            // Mode-specific Physics
            if (player.mode === 'CUBE') {
                player.vy += GRAVITY * player.gravityDir;
                player.y += player.vy;

                // Rotation animation when jumping
                if (!player.isGrounded) {
                    player.rotation += 8 * player.gravityDir;
                } else {
                    player.rotation = Math.round(player.rotation / 90) * 90;
                }

                // Floor collision
                if (player.y >= FLOOR_Y - PLAYER_SIZE) {
                    player.y = FLOOR_Y - PLAYER_SIZE;
                    player.vy = 0;
                    player.isGrounded = true;
                }

                // Buffer jump on hold
                if (isHoldingInput && player.isGrounded) {
                    player.vy = JUMP_FORCE * player.gravityDir;
                    player.isGrounded = false;
                    playSound('jump');
                }

            } else if (player.mode === 'SHIP') {
                // Fly up when holding input, fall down when released
                let shipAccel = isHoldingInput ? -0.85 : 0.7;
                player.vy += shipAccel;
                player.vy = Math.max(-9, Math.min(9, player.vy));
                player.y += player.vy;

                // Rotation proportional to vertical velocity
                player.rotation = player.vy * 4;

                // Ceiling/Floor Bounds
                if (player.y <= CEILING_Y) {
                    player.y = CEILING_Y;
                    player.vy = 0;
                }
                if (player.y >= FLOOR_Y - PLAYER_SIZE) {
                    player.y = FLOOR_Y - PLAYER_SIZE;
                    player.vy = 0;
                }

            } else if (player.mode === 'WAVE') {
                // Fix: Continuous 45-degree sharp zigzag physics
                let waveSpeedY = 8.5;
                if (isHoldingInput) {
                    player.vy = -waveSpeedY;
                } else {
                    player.vy = waveSpeedY;
                }
                player.y += player.vy;

                // Angle points sharply in diagonal direction
                player.rotation = isHoldingInput ? -45 : 45;

                // Fix: Push trail coordinates safely
                player.waveTrail.push({
                    x: player.x + PLAYER_SIZE / 2,
                    y: player.y + PLAYER_SIZE / 2
                });

                // Limit trail length to prevent memory leaks or rendering freezes
                if (player.waveTrail.length > 250) {
                    player.waveTrail.shift();
                }

                // Wave Mode dies if it hits Floor or Ceiling
                if (player.y <= CEILING_Y || player.y >= FLOOR_Y - PLAYER_SIZE) {
                    die();
                    return;
                }
            }

            // Camera follow smoothly
            cameraX = player.x - 180;

            // --- Collisions with Blocks & Pads ---
            player.isGrounded = false;

            for (let obj of levelObjects) {
                // Skip offscreen objects for performance
                if (obj.x + obj.w < cameraX - 100 || obj.x > cameraX + canvas.width + 100) continue;

                // Player Hitbox (slightly smaller for forgiving gameplay)
                let pBox = {
                    x: player.x + 4,
                    y: player.y + 4,
                    w: PLAYER_SIZE - 8,
                    h: PLAYER_SIZE - 8
                };

                // 1. Spikes Collision
                if (obj.type === 'spike' || obj.type === 'spike_down') {
                    // Triangle-like tight hitbox for enlarged spikes
                    let spikeHitbox = {
                        x: obj.x + 6,
                        y: obj.y + 6,
                        w: obj.w - 12,
                        h: obj.h - 12
                    };

                    if (checkAABB(pBox, spikeHitbox)) {
                        die();
                        return;
                    }
                }

                // 2. Solid Blocks Collision
                else if (obj.type === 'block') {
                    if (checkAABB(pBox, obj)) {
                        // Determine collision side
                        let prevY = player.y - player.vy;

                        // Landing on top
                        if (prevY + PLAYER_SIZE <= obj.y + 12 && player.vy >= 0) {
                            player.y = obj.y - PLAYER_SIZE;
                            player.vy = 0;
                            player.isGrounded = true;
                        } 
                        // Hitting ceiling/bottom of block
                        else if (prevY >= obj.y + obj.h - 12 && player.vy <= 0) {
                            player.y = obj.y + obj.h;
                            player.vy = 0;
                        } 
                        // Hitting the side = Death
                        else {
                            die();
                            return;
                        }
                    }
                }

                // 3. Jump Pads Collision (Improved trigger mechanism)
                else if (obj.type === 'pad_yellow' || obj.type === 'pad_blue') {
                    // Generous trigger box for jump pads
                    let padTrigger = {
                        x: obj.x - 6,
                        y: obj.y - 10,
                        w: obj.w + 12,
                        h: obj.h + 16
                    };

                    if (checkAABB(pBox, padTrigger)) {
                        if (obj.type === 'pad_yellow') {
                            player.vy = -16.5 * player.gravityDir;
                            player.isGrounded = false;
                            playSound('pad');
                            createParticles(obj.x + obj.w/2, obj.y, 12, '#ffe600');
                        } else if (obj.type === 'pad_blue') {
                            player.gravityDir *= -1;
                            player.vy = -8 * player.gravityDir;
                            playSound('pad');
                            createParticles(obj.x + obj.w/2, obj.y, 12, '#00f0ff');
                        }
                    }
                }

                // 4. Mode Switch Portals
                else if (obj.type.startsWith('portal_')) {
                    if (checkAABB(pBox, obj)) {
                        let newMode = obj.type.replace('portal_', '').toUpperCase();
                        if (player.mode !== newMode) {
                            player.mode = newMode;
                            player.waveTrail = [];
                            playSound('portal');
                            createParticles(player.x, player.y, 15, '#ff007f');

                            modeBadge.innerText = player.mode;
                            modeBadge.style.borderColor = player.mode === 'WAVE' ? '#ff007f' : (player.mode === 'SHIP' ? '#ffe600' : '#00f0ff');
                            modeBadge.style.color = modeBadge.style.borderColor;
                        }
                    }
                }
            }

            // Update Particle FX
            updateParticles();

            // Progress HUD Update
            let percent = Math.min(100, Math.floor((player.x / LEVEL_LENGTH) * 100));
            progressBar.style.width = percent + '%';
            percentText.innerText = percent + '%';

            // Check Level Win
            if (player.x >= LEVEL_LENGTH) {
                gameState = 'WIN';
                deathMessage.innerText = 'LEVEL CLEARED! 100%';
                deathScreen.style.display = 'flex';
            }
        }

        // Helper AABB Box Collision
        function checkAABB(a, b) {
            return (
                a.x < b.x + b.w &&
                a.x + a.w > b.x &&
                a.y < b.y + b.h &&
                a.y + a.h > b.y
            );
        }

        // --- Render Functions ---
        function render() {
            // Fix: Reset canvas state cleanly to prevent Black Screen glitch
            ctx.restore();
            ctx.save();

            // 1. Clear Screen & Dynamic Background
            let bgHue = (player.x * 0.02) % 360;
            ctx.fillStyle = `hsl(${bgHue}, 40%, 8%)`;
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Background Grid Lines
            ctx.strokeStyle = `hsl(${bgHue}, 50%, 15%)`;
            ctx.lineWidth = 1;
            let gridOffset = (cameraX * 0.3) % 40;
            for (let x = -gridOffset; x < canvas.width; x += 40) {
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, canvas.height);
                ctx.stroke();
            }

            // 2. Draw Floor & Ceiling
            ctx.fillStyle = '#0f111a';
            ctx.fillRect(0, FLOOR_Y, canvas.width, canvas.height - FLOOR_Y);
            ctx.fillRect(0, 0, canvas.width, CEILING_Y);

            // Floor Neon Line
            ctx.strokeStyle = '#00f0ff';
            ctx.lineWidth = 3;
            ctx.shadowColor = '#00f0ff';
            ctx.shadowBlur = 12;
            ctx.beginPath();
            ctx.moveTo(0, FLOOR_Y);
            ctx.lineTo(canvas.width, FLOOR_Y);
            ctx.moveTo(0, CEILING_Y);
            ctx.lineTo(canvas.width, CEILING_Y);
            ctx.stroke();
            ctx.shadowBlur = 0; // Reset shadow

            // 3. Draw Level Objects
            for (let obj of levelObjects) {
                if (obj.x + obj.w < cameraX - 100 || obj.x > cameraX + canvas.width + 100) continue;

                let drawX = obj.x - cameraX;

                // Spike Rendering (Enlarged and Glowing)
                if (obj.type === 'spike') {
                    ctx.fillStyle = '#222';
                    ctx.strokeStyle = '#ff0055';
                    ctx.lineWidth = 3;

                    ctx.beginPath();
                    ctx.moveTo(drawX, obj.y + obj.h);
                    ctx.lineTo(drawX + obj.w / 2, obj.y);
                    ctx.lineTo(drawX + obj.w, obj.y + obj.h);
                    ctx.closePath();
                    ctx.fill();
                    ctx.stroke();

                    // Inner detail
                    ctx.fillStyle = '#ff0055';
                    ctx.beginPath();
                    ctx.moveTo(drawX + obj.w * 0.3, obj.y + obj.h - 4);
                    ctx.lineTo(drawX + obj.w / 2, obj.y + obj.h * 0.4);
                    ctx.lineTo(drawX + obj.w * 0.7, obj.y + obj.h - 4);
                    ctx.closePath();
                    ctx.fill();

                } else if (obj.type === 'spike_down') {
                    ctx.fillStyle = '#222';
                    ctx.strokeStyle = '#ff0055';
                    ctx.lineWidth = 3;

                    ctx.beginPath();
                    ctx.moveTo(drawX, obj.y);
                    ctx.lineTo(drawX + obj.w / 2, obj.y + obj.h);
                    ctx.lineTo(drawX + obj.w, obj.y);
                    ctx.closePath();
                    ctx.fill();
                    ctx.stroke();

                } else if (obj.type === 'block') {
                    ctx.fillStyle = '#151828';
                    ctx.strokeStyle = '#00f0ff';
                    ctx.lineWidth = 2;
                    ctx.fillRect(drawX, obj.y, obj.w, obj.h);
                    ctx.strokeRect(drawX, obj.y, obj.w, obj.h);

                    // Block Grid pattern
                    ctx.strokeStyle = 'rgba(0, 240, 255, 0.2)';
                    ctx.strokeRect(drawX + 4, obj.y + 4, obj.w - 8, obj.h - 8);

                } else if (obj.type === 'pad_yellow') {
                    ctx.fillStyle = '#ffe600';
                    ctx.shadowColor = '#ffe600';
                    ctx.shadowBlur = 10;
                    ctx.beginPath();
                    ctx.ellipse(drawX + obj.w/2, obj.y + obj.h/2, obj.w/2, obj.h/2, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.shadowBlur = 0;

                } else if (obj.type === 'pad_blue') {
                    ctx.fillStyle = '#00f0ff';
                    ctx.shadowColor = '#00f0ff';
                    ctx.shadowBlur = 10;
                    ctx.beginPath();
                    ctx.ellipse(drawX + obj.w/2, obj.y + obj.h/2, obj.w/2, obj.h/2, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.shadowBlur = 0;

                } else if (obj.type.startsWith('portal_')) {
                    let color = obj.type.includes('wave') ? '#ff007f' : (obj.type.includes('ship') ? '#ffe600' : '#00f0ff');
                    ctx.strokeStyle = color;
                    ctx.lineWidth = 4;
                    ctx.shadowColor = color;
                    ctx.shadowBlur = 15;
                    ctx.strokeRect(drawX, obj.y, obj.w, obj.h);
                    ctx.shadowBlur = 0;
                }
            }

            // 4. Draw Practice Checkpoints
            if (isPracticeMode) {
                checkpoints.forEach(cp => {
                    if (cp.x - cameraX > -50 && cp.x - cameraX < canvas.width + 50) {
                        ctx.fillStyle = '#00ff66';
                        ctx.beginPath();
                        ctx.arc(cp.x - cameraX, cp.y + 18, 10, 0, Math.PI * 2);
                        ctx.fill();
                    }
                });
            }

            // 5. Wave Mode Trail (Fix: Safe Canvas Path Drawing)
            if (player.mode === 'WAVE' && player.waveTrail.length > 1) {
                ctx.save();
                ctx.strokeStyle = '#ff007f';
                ctx.lineWidth = 5;
                ctx.shadowColor = '#ff007f';
                ctx.shadowBlur = 12;
                ctx.beginPath();

                for (let i = 0; i < player.waveTrail.length; i++) {
                    let pt = player.waveTrail[i];
                    let tx = pt.x - cameraX;
                    let ty = pt.y;

                    if (i === 0) {
                        ctx.moveTo(tx, ty);
                    } else {
                        ctx.lineTo(tx, ty);
                    }
                }
                ctx.stroke();
                ctx.restore();
            }

            // 6. Draw Player
            if (gameState === 'PLAYING') {
                ctx.save();
                let screenPlayerX = player.x - cameraX + PLAYER_SIZE / 2;
                let screenPlayerY = player.y + PLAYER_SIZE / 2;

                ctx.translate(screenPlayerX, screenPlayerY);
                ctx.rotate((player.rotation * Math.PI) / 180);

                if (player.mode === 'CUBE') {
                    // Cube Body
                    ctx.fillStyle = '#ffe600';
                    ctx.strokeStyle = '#000';
                    ctx.lineWidth = 3;
                    ctx.fillRect(-PLAYER_SIZE / 2, -PLAYER_SIZE / 2, PLAYER_SIZE, PLAYER_SIZE);
                    ctx.strokeRect(-PLAYER_SIZE / 2, -PLAYER_SIZE / 2, PLAYER_SIZE, PLAYER_SIZE);

                    // Inner Face Squares
                    ctx.fillStyle = '#00f0ff';
                    ctx.fillRect(-8, -8, 16, 16);

                } else if (player.mode === 'SHIP') {
                    // Ship Shape
                    ctx.fillStyle = '#ffe600';
                    ctx.beginPath();
                    ctx.moveTo(-PLAYER_SIZE / 2, PLAYER_SIZE / 4);
                    ctx.lineTo(PLAYER_SIZE / 2, 0);
                    ctx.lineTo(-PLAYER_SIZE / 2, -PLAYER_SIZE / 4);
                    ctx.closePath();
                    ctx.fill();

                    // Bubble Dome
                    ctx.fillStyle = '#00f0ff';
                    ctx.beginPath();
                    ctx.arc(-2, -2, 8, 0, Math.PI * 2);
                    ctx.fill();

                } else if (player.mode === 'WAVE') {
                    // Arrow / Wave Shape
                    ctx.fillStyle = '#ff007f';
                    ctx.strokeStyle = '#ffffff';
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    ctx.moveTo(PLAYER_SIZE / 2, 0);
                    ctx.lineTo(-PLAYER_SIZE / 2, -PLAYER_SIZE / 2.2);
                    ctx.lineTo(-PLAYER_SIZE / 4, 0);
                    ctx.lineTo(-PLAYER_SIZE / 2, PLAYER_SIZE / 2.2);
                    ctx.closePath();
                    ctx.fill();
                    ctx.stroke();
                }

                ctx.restore();
            }

            // 7. Draw Particles
            drawParticles();

            ctx.restore();
        }

        // Main Loop
        function gameLoop() {
            update();
            render();
            requestAnimationFrame(gameLoop);
        }

        // Start initialization
        generateLevel();
        gameLoop();
    </script>
</body>
</html>
