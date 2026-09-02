import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="미니 냥코대전쟁", layout="centered")
st.title("🐱 미니 냥코대전쟁")

game_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            background-color: #f0f0f0;
            font-family: sans-serif;
        }
        .game-container {
            position: relative;
            width: 800px;
        }
        canvas {
            border: 2px solid #333;
            background-color: #e0f7fa;
            display: block;
        }
        .top-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 800px;
            margin: 10px 0;
        }
        .left-group {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .settings-btn {
            background-color: #607d8b;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 16px;
            cursor: pointer;
            font-weight: bold;
        }
        .settings-btn:hover {
            background-color: #455a64;
        }
        .money-display {
            font-size: 18px;
            font-weight: bold;
            color: #2e7d32;
        }
        .stage-title {
            font-size: 18px;
            font-weight: bold;
            color: #1565c0;
        }

        /* 캔버스 중앙 오버레이 */
        .center-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 800px;
            height: 300px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            background-color: rgba(0, 0, 0, 0.4);
            z-index: 5;
        }

        .action-btn {
            padding: 12px 24px;
            font-size: 16px;
            font-weight: bold;
            color: #fff;
            background-color: #ff9800;
            border: 2px solid #e65100;
            border-radius: 8px;
            cursor: pointer;
            margin-top: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        }
        .action-btn:hover {
            background-color: #f57c00;
        }
        .next-btn {
            background-color: #4caf50;
            border-color: #2e7d32;
        }

        .controls {
            display: flex;
            gap: 12px;
            margin-top: 5px;
            justify-content: center;
            width: 800px;
        }
        .unit-slot {
            position: relative;
            width: 75px;
            height: 75px;
            background-color: #ffffff;
            border: 2px solid #333;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
            user-select: none;
            overflow: hidden;
            box-sizing: border-box;
        }
        .unit-slot.disabled {
            cursor: not-allowed;
            background-color: #e0e0e0;
            color: #888;
        }
        .unit-slot.empty {
            background-color: #eceff1;
            border: 2px dashed #b0bec5;
            cursor: default;
            color: #b0bec5;
        }
        
        .cooldown-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.55);
            pointer-events: none;
            transition: height 0.05s linear;
        }
        .cost-tag {
            font-size: 11px;
            color: #d32f2f;
            margin-top: 2px;
        }

        /* 팝업 모달공통 */
        .modal {
            display: none;
            position: absolute;
            top: 25px;
            left: 200px;
            width: 400px;
            background: #ffffff;
            border: 3px solid #333;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
            text-align: center;
            padding: 20px;
            z-index: 10;
            box-sizing: border-box;
        }
        .modal h2 {
            margin: 0 0 15px 0;
            color: #333;
            font-size: 20px;
        }
        .setting-item {
            margin: 15px 0;
            display: flex;
            flex-direction: column;
            gap: 8px;
            align-items: center;
        }
        .setting-btn-group {
            display: flex;
            flex-direction: column;
            gap: 10px;
            width: 100%;
        }
        .modal-btn {
            padding: 10px;
            font-size: 14px;
            font-weight: bold;
            border-radius: 6px;
            border: none;
            cursor: pointer;
            color: white;
        }
        .btn-resume { background-color: #4caf50; }
        .btn-home { background-color: #2196f3; }
        
        /* 홈 화면 오버레이 */
        .home-screen {
            display: none;
            position: absolute;
            top: 0;
            left: 0;
            width: 800px;
            height: 300px;
            background: #eceff1;
            z-index: 20;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            border: 2px solid #333;
            box-sizing: border-box;
        }
    </style>
</head>
<body>
    <div class="top-bar">
        <div class="left-group">
            <button class="settings-btn" onclick="openSettings()">⚙️ 설정</button>
            <div class="money-display">💰 소지금: <span id="moneyTxt">0</span>원 / 1000원</div>
        </div>
        <div class="stage-title" id="stageTxt">🚩 Stage 1</div>
    </div>

    <div class="game-container">
        <canvas id="gameCanvas" width="800" height="300"></canvas>
        
        <!-- 중앙 게임시작 오버레이 -->
        <div id="centerOverlay" class="center-overlay">
            <h2 id="overlayMsg" style="color: white; margin: 0; font-size: 24px;">⚔️ 미니 냥코대전쟁</h2>
            <button id="btnStartCenter" class="action-btn" onclick="startGame()">⚔️ 게임 시작</button>
            <button id="btnNextCenter" class="action-btn next-btn" style="display: none;" onclick="showRewardModal()">➡️ 다음 스테이지</button>
        </div>

        <!-- 설정 모달 -->
        <div id="settingsModal" class="modal">
            <h2>⚙️ 설정</h2>
            <div class="setting-item">
                <label for="volumeRange"><b>🔊 소리 조절</b></label>
                <input type="range" id="volumeRange" min="0" max="1" step="0.05" value="0.3" oninput="changeVolume(this.value)">
            </div>
            <div class="setting-btn-group">
                <button class="modal-btn btn-resume" onclick="closeSettings()">▶️ 계속하기 (다시시작)</button>
                <button class="modal-btn btn-home" onclick="goToHome()">🏠 홈으로</button>
            </div>
        </div>

        <!-- 캐릭터 획득 팝업 창 -->
        <div id="rewardModal" class="modal">
            <h2>🎉 캐릭터 해금!</h2>
            <p><b>[🪓 도끼맨]</b>을(를) 획득했습니다!<br>사거리가 긴 신규 원거리 딜러 캐릭터입니다.</p>
            <button class="action-btn next-btn" onclick="closeModalAndStartStage2()">➡️ Stage 2 시작하기</button>
        </div>

        <!-- 홈 화면 창 -->
        <div id="homeScreen" class="home-screen">
            <h1>🐱 미니 냥코대전쟁 홈</h1>
            <p style="color: #666;">(홈 화면 기능은 추후 업데이트 예정입니다)</p>
            <button class="action-btn" onclick="leaveHomeToStage()">🎮 스테이지 선택으로 이동</button>
        </div>
    </div>

    <div class="controls">
        <div id="slotBasic" class="unit-slot disabled" onclick="spawnPlayerUnit('basic')">
            <div>🐱 기본</div>
            <div class="cost-tag">50원</div>
            <div id="cdBasic" class="cooldown-overlay" style="height: 0%;"></div>
        </div>

        <div id="slotTank" class="unit-slot disabled" onclick="spawnPlayerUnit('tank')">
            <div>🦒 탱커</div>
            <div class="cost-tag">75원</div>
            <div id="cdTank" class="cooldown-overlay" style="height: 0%;"></div>
        </div>

        <div id="slotAxe" class="unit-slot disabled" style="display: none;" onclick="spawnPlayerUnit('axe')">
            <div>🪓 도끼맨</div>
            <div class="cost-tag">100원</div>
            <div id="cdAxe" class="cooldown-overlay" style="height: 0%;"></div>
        </div>

        <div id="slotEmpty4" class="unit-slot empty">
            <div>EMPTY</div>
        </div>
    </div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        const groundY = 220;

        let currentStage = 1;
        let gameStarted = false;
        let gameOver = false;
        let gameWon = false;
        let isPaused = false;

        let money = 0;
        const maxMoney = 1000;
        const moneyIncomeRate = 0.5;

        // Sound System (Web Audio API)
        let audioCtx = null;
        let masterGain = null;
        let bgmInterval = null;
        let masterVolume = 0.3;

        function initAudio() {
            if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                masterGain = audioCtx.createGain();
                masterGain.gain.value = masterVolume;
                masterGain.connect(audioCtx.destination);
                startBGM();
            }
        }

        function changeVolume(val) {
            masterVolume = parseFloat(val);
            if (masterGain) {
                masterGain.gain.value = masterVolume;
            }
        }

        function playSpawnSound() {
            if (!audioCtx) return;
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(400, audioCtx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(800, audioCtx.currentTime + 0.1);
            gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
            gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);
            osc.connect(gain);
            gain.connect(masterGain);
            osc.start();
            osc.stop(audioCtx.currentTime + 0.1);
        }

        function playBossSound() {
            if (!audioCtx) return;
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(120, audioCtx.currentTime);
            osc.frequency.linearRampToValueAtTime(60, audioCtx.currentTime + 0.6);
            gain.gain.setValueAtTime(0.5, audioCtx.currentTime);
            gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.6);
            osc.connect(gain);
            gain.connect(masterGain);
            osc.start();
            osc.stop(audioCtx.currentTime + 0.6);
        }

        function startBGM() {
            if (bgmInterval) return;
            let noteIndex = 0;
            const notes = [261.63, 329.63, 392.00, 523.25]; // C E G C
            bgmInterval = setInterval(() => {
                if (!gameStarted || isPaused || gameOver || !audioCtx) return;
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'triangle';
                osc.frequency.setValueAtTime(notes[noteIndex], audioCtx.currentTime);
                gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
                gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.2);
                osc.connect(gain);
                gain.connect(masterGain);
                osc.start();
                osc.stop(audioCtx.currentTime + 0.2);
                noteIndex = (noteIndex + 1) % notes.length;
            }, 300);
        }

        const playerUnitConfigs = {
            basic: { cost: 50,  cooldown: 500,  hp: 30, atk: 10, speed: 1.2, width: 25, height: 25, range: 5,   color: '#ffffff', atkCooldown: 60 },
            tank:  { cost: 75,  cooldown: 1000, hp: 60, atk: 7,  speed: 0.6, width: 20, height: 50, range: 5,   color: '#ffffff', atkCooldown: 80 },
            axe:   { cost: 100, cooldown: 2000, hp: 20, atk: 25, speed: 1.0, width: 25, height: 30, range: 125, color: '#ff7043', atkCooldown: 70 }
        };

        const enemyUnitConfigs = {
            doge:  { hp: 20,  atk: 8,  speed: 0.9, width: 25, height: 25, color: '#ffcc80', atkCooldown: 60 },
            snake: { hp: 17,  atk: 11, speed: 1.4, width: 35, height: 15, color: '#a5d6a7', atkCooldown: 50 },
            hippo: { hp: 300, atk: 20, speed: 0.5, width: 50, height: 40, color: '#f8bbd0', atkCooldown: 45 }
        };

        const cooldownState = {
            basic: { ready: true, remaining: 0, total: 500 },
            tank:  { ready: true, remaining: 0, total: 1000 },
            axe:   { ready: true, remaining: 0, total: 2000 }
        };

        let playerCastle = { x: 690, y: groundY - 80, width: 60, height: 80, hp: 200, maxHp: 200 };
        let enemyCastle = { x: 50, y: groundY - 80, width: 60, height: 80, hp: 200, maxHp: 200 };

        let playerUnits = [];
        let enemyUnits = [];

        let lastEnemySpawnTime = Date.now();
        let bossSpawned = false;
        let waveEffect = { active: false, radius: 0, maxRadius: 300 };

        function openSettings() {
            initAudio();
            isPaused = true;
            document.getElementById("settingsModal").style.display = "block";
        }

        function closeSettings() {
            isPaused = false;
            document.getElementById("settingsModal").style.display = "none";
        }

        function goToHome() {
            document.getElementById("settingsModal").style.display = "none";
            document.getElementById("homeScreen").style.display = "flex";
            isPaused = true;
        }

        function leaveHomeToStage() {
            document.getElementById("homeScreen").style.display = "none";
            initStage(currentStage);
        }

        function initStage(stageNum) {
            currentStage = stageNum;
            gameStarted = false;
            gameOver = false;
            gameWon = false;
            isPaused = false;
            bossSpawned = false;
            money = 0;

            playerCastle.hp = 200;
            enemyCastle.hp = 200;

            playerUnits = [];
            enemyUnits = [];

            document.getElementById("stageTxt").innerText = "🚩 Stage " + currentStage;
            document.getElementById("centerOverlay").style.display = "flex";
            document.getElementById("overlayMsg").innerText = "🚩 Stage " + currentStage;
            document.getElementById("btnStartCenter").style.display = "inline-block";
            document.getElementById("btnNextCenter").style.display = "none";

            if (currentStage >= 2) {
                document.getElementById("slotAxe").style.display = "flex";
            } else {
                document.getElementById("slotAxe").style.display = "none";
            }
        }

        function startGame() {
            initAudio();
            if (gameStarted) return;
            gameStarted = true;
            isPaused = false;
            document.getElementById("centerOverlay").style.display = "none";
            lastEnemySpawnTime = Date.now();
        }

        function showRewardModal() {
            document.getElementById("centerOverlay").style.display = "none";
            document.getElementById("rewardModal").style.display = "block";
        }

        function closeModalAndStartStage2() {
            document.getElementById("rewardModal").style.display = "none";
            initStage(2);
        }

        function triggerCooldown(type) {
            const config = playerUnitConfigs[type];
            cooldownState[type].ready = false;
            cooldownState[type].total = config.cooldown;
            cooldownState[type].remaining = config.cooldown;

            const interval = 20;
            const timer = setInterval(() => {
                if (!isPaused) {
                    cooldownState[type].remaining -= interval;
                    if (cooldownState[type].remaining <= 0) {
                        cooldownState[type].remaining = 0;
                        cooldownState[type].ready = true;
                        clearInterval(timer);
                    }
                }
            }, interval);
        }

        function spawnPlayerUnit(type) {
            if (!gameStarted || gameOver || isPaused) return;
            if (type === 'axe' && currentStage < 2) return;

            const config = playerUnitConfigs[type];

            if (money < config.cost || !cooldownState[type].ready) return;

            money -= config.cost;
            playSpawnSound();
            triggerCooldown(type);

            playerUnits.push({
                type: type,
                x: playerCastle.x - config.width,
                y: groundY - config.height,
                width: config.width,
                height: config.height,
                speed: config.speed,
                hp: config.hp,
                maxHp: config.hp,
                atk: config.atk,
                range: config.range,
                color: config.color,
                atkTimer: 0,
                atkCooldown: config.atkCooldown
            });
        }

        function spawnBossHippo() {
            bossSpawned = true;
            playBossSound();
            const config = enemyUnitConfigs.hippo;

            enemyUnits.push({
                x: enemyCastle.x + enemyCastle.width,
                y: groundY - config.height,
                width: config.width,
                height: config.height,
                speed: config.speed,
                hp: config.hp,
                maxHp: config.hp,
                atk: config.atk,
                color: config.color,
                atkTimer: 0,
                atkCooldown: config.atkCooldown,
                isBoss: true
            });

            waveEffect.active = true;
            waveEffect.radius = 0;

            playerUnits.forEach(pUnit => {
                pUnit.x = Math.min(playerCastle.x - pUnit.width, pUnit.x + 180);
            });
        }

        function spawnEnemyUnit() {
            if (!gameStarted || gameOver || isPaused) return;

            if (currentStage === 2 && !bossSpawned && enemyCastle.hp <= enemyCastle.maxHp / 2) {
                spawnBossHippo();
            }

            const now = Date.now();
            if (now - lastEnemySpawnTime > Math.random() * 1500 + 2500) {
                lastEnemySpawnTime = now;

                const spawnCount = Math.random() < 0.2 ? 2 : 1;
                for (let i = 0; i < spawnCount; i++) {
                    const isDoge = Math.random() < 0.6;
                    const config = isDoge ? enemyUnitConfigs.doge : enemyUnitConfigs.snake;

                    enemyUnits.push({
                        x: enemyCastle.x + enemyCastle.width + (i * 20),
                        y: groundY - config.height,
                        width: config.width,
                        height: config.height,
                        speed: config.speed,
                        hp: config.hp,
                        maxHp: config.hp,
                        atk: config.atk,
                        color: config.color,
                        atkTimer: 0,
                        atkCooldown: config.atkCooldown,
                        isBoss: false
                    });
                }
            }
        }

        function updateUI() {
            document.getElementById("moneyTxt").innerText = Math.floor(money);

            const slotBasic = document.getElementById("slotBasic");
            const cdBasic = document.getElementById("cdBasic");
            cdBasic.style.height = ((cooldownState.basic.remaining / cooldownState.basic.total) * 100) + "%";
            if (gameStarted && !gameOver && !isPaused && money >= playerUnitConfigs.basic.cost && cooldownState.basic.ready) {
                slotBasic.classList.remove("disabled");
            } else {
                slotBasic.classList.add("disabled");
            }

            const slotTank = document.getElementById("slotTank");
            const cdTank = document.getElementById("cdTank");
            cdTank.style.height = ((cooldownState.tank.remaining / cooldownState.tank.total) * 100) + "%";
            if (gameStarted && !gameOver && !isPaused && money >= playerUnitConfigs.tank.cost && cooldownState.tank.ready) {
                slotTank.classList.remove("disabled");
            } else {
                slotTank.classList.add("disabled");
            }

            const slotAxe = document.getElementById("slotAxe");
            const cdAxe = document.getElementById("cdAxe");
            cdAxe.style.height = ((cooldownState.axe.remaining / cooldownState.axe.total) * 100) + "%";
            if (gameStarted && !gameOver && !isPaused && currentStage >= 2 && money >= playerUnitConfigs.axe.cost && cooldownState.axe.ready) {
                slotAxe.classList.remove("disabled");
            } else {
                slotAxe.classList.add("disabled");
            }
        }

        function update() {
            if (!gameStarted || gameOver || isPaused) {
                updateUI();
                return;
            }

            if (money < maxMoney) {
                money = Math.min(maxMoney, money + moneyIncomeRate);
            }

            spawnEnemyUnit();

            if (waveEffect.active) {
                waveEffect.radius += 12;
                if (waveEffect.radius >= waveEffect.maxRadius) {
                    waveEffect.active = false;
                }
            }

            playerUnits.forEach((pUnit) => {
                let targetEnemy = null;
                for (let eUnit of enemyUnits) {
                    if (eUnit.x + eUnit.width < pUnit.x && eUnit.x + eUnit.width >= pUnit.x - pUnit.range) {
                        targetEnemy = eUnit;
                        break;
                    }
                }

                if (targetEnemy) {
                    pUnit.atkTimer++;
                    if (pUnit.atkTimer >= pUnit.atkCooldown) {
                        pUnit.atkTimer = 0;
                        targetEnemy.hp -= pUnit.atk;
                    }
                } else if (pUnit.x - pUnit.range <= enemyCastle.x + enemyCastle.width) {
                    pUnit.atkTimer++;
                    if (pUnit.atkTimer >= pUnit.atkCooldown) {
                        pUnit.atkTimer = 0;
                        enemyCastle.hp = Math.max(0, enemyCastle.hp - pUnit.atk);
                    }
                } else {
                    pUnit.x -= pUnit.speed;
                }
            });

            enemyUnits.forEach((eUnit) => {
                let targetPlayer = null;
                for (let pUnit of playerUnits) {
                    if (pUnit.x <= eUnit.x + eUnit.width + 5 && pUnit.x + pUnit.width > eUnit.x) {
                        targetPlayer = pUnit;
                        break;
                    }
                }

                if (targetPlayer) {
                    eUnit.atkTimer++;
                    if (eUnit.atkTimer >= eUnit.atkCooldown) {
                        eUnit.atkTimer = 0;
                        targetPlayer.hp -= eUnit.atk;
                    }
                } else if (eUnit.x + eUnit.width >= playerCastle.x) {
                    eUnit.atkTimer++;
                    if (eUnit.atkTimer >= eUnit.atkCooldown) {
                        eUnit.atkTimer = 0;
                        playerCastle.hp = Math.max(0, playerCastle.hp - eUnit.atk);
                    }
                } else {
                    eUnit.x += eUnit.speed;
                }
            });

            for (let i = playerUnits.length - 1; i >= 0; i--) {
                if (playerUnits[i].hp <= 0) playerUnits.splice(i, 1);
            }
            for (let i = enemyUnits.length - 1; i >= 0; i--) {
                if (enemyUnits[i].hp <= 0) enemyUnits.splice(i, 1);
            }

            if (enemyCastle.hp <= 0) {
                gameOver = true;
                gameWon = true;
                document.getElementById("centerOverlay").style.display = "flex";
                if (currentStage === 1) {
                    document.getElementById("overlayMsg").innerText = "🎉 STAGE 1 CLEAR!";
                    document.getElementById("btnStartCenter").style.display = "none";
                    document.getElementById("btnNextCenter").style.display = "inline-block";
                } else {
                    document.getElementById("overlayMsg").innerText = "🏆 ALL STAGE CLEAR!";
                    document.getElementById("btnStartCenter").style.display = "none";
                    document.getElementById("btnNextCenter").style.display = "none";
                }
            } else if (playerCastle.hp <= 0) {
                gameOver = true;
                gameWon = false;
                document.getElementById("centerOverlay").style.display = "flex";
                document.getElementById("overlayMsg").innerText = "💀 DEFEAT... (패배)";
                document.getElementById("btnStartCenter").style.display = "none";
                document.getElementById("btnNextCenter").style.display = "none";
            }

            updateUI();
        }

        function render() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            ctx.fillStyle = "#81c784";
            ctx.fillRect(0, groundY, canvas.width, canvas.height - groundY);
            ctx.strokeStyle = "#388e3c";
            ctx.lineWidth = 4;
            ctx.beginPath();
            ctx.moveTo(0, groundY);
            ctx.lineTo(canvas.width, groundY);
            ctx.stroke();

            ctx.fillStyle = "#ef5350";
            ctx.fillRect(enemyCastle.x, enemyCastle.y, enemyCastle.width, enemyCastle.height);
            ctx.fillStyle = "#e53935";
            ctx.beginPath();
            ctx.moveTo(enemyCastle.x - 10, enemyCastle.y);
            ctx.lineTo(enemyCastle.x + enemyCastle.width / 2, enemyCastle.y - 30);
            ctx.lineTo(enemyCastle.x + enemyCastle.width + 10, enemyCastle.y);
            ctx.closePath();
            ctx.fill();

            ctx.fillStyle = "#42a5f5";
            ctx.fillRect(playerCastle.x, playerCastle.y, playerCastle.width, playerCastle.height);
            ctx.fillStyle = "#1e88e5";
            ctx.beginPath();
            ctx.moveTo(playerCastle.x - 10, playerCastle.y);
            ctx.lineTo(playerCastle.x + playerCastle.width / 2, playerCastle.y - 30);
            ctx.lineTo(playerCastle.x + playerCastle.width + 10, playerCastle.y);
            ctx.closePath();
            ctx.fill();

            ctx.fillStyle = "#000000";
            ctx.font = "bold 13px sans-serif";
            ctx.textAlign = "center";
            ctx.fillText("적군 성 (" + enemyCastle.hp + "/" + enemyCastle.maxHp + ")", enemyCastle.x + enemyCastle.width / 2, enemyCastle.y - 40);
            ctx.fillText("아군 성 (" + playerCastle.hp + "/" + playerCastle.maxHp + ")", playerCastle.x + playerCastle.width / 2, playerCastle.y - 40);

            ctx.fillStyle = "#e0e0e0";
            ctx.fillRect(enemyCastle.x, enemyCastle.y - 35, enemyCastle.width, 6);
            ctx.fillRect(playerCastle.x, playerCastle.y - 35, playerCastle.width, 6);
            
            ctx.fillStyle = "#4caf50";
            ctx.fillRect(enemyCastle.x, enemyCastle.y - 35, enemyCastle.width * (enemyCastle.hp / enemyCastle.maxHp), 6);
            ctx.fillRect(playerCastle.x, playerCastle.y - 35, playerCastle.width * (playerCastle.hp / playerCastle.maxHp), 6);

            playerUnits.forEach(unit => {
                ctx.fillStyle = unit.color;
                ctx.fillRect(unit.x, unit.y, unit.width, unit.height);
                ctx.strokeStyle = '#000000';
                ctx.lineWidth = 2;
                ctx.strokeRect(unit.x, unit.y, unit.width, unit.height);

                ctx.fillStyle = "#ffffff";
                ctx.beginPath();
                ctx.moveTo(unit.x, unit.y);
                ctx.lineTo(unit.x + 4, unit.y - 6);
                ctx.lineTo(unit.x + 8, unit.y);
                ctx.fill();
                ctx.stroke();

                ctx.beginPath();
                ctx.moveTo(unit.x + unit.width - 8, unit.y);
                ctx.lineTo(unit.x + unit.width - 4, unit.y - 6);
                ctx.lineTo(unit.x + unit.width, unit.y);
                ctx.fill();
                ctx.stroke();

                if (unit.type === 'axe' && unit.atkTimer > unit.atkCooldown - 15) {
                    ctx.strokeStyle = "#d84315";
                    ctx.lineWidth = 3;
                    ctx.beginPath();
                    ctx.moveTo(unit.x, unit.y + 10);
                    ctx.lineTo(unit.x - unit.range, unit.y + 10);
                    ctx.stroke();
                }

                ctx.fillStyle = "#ff5252";
                ctx.fillRect(unit.x, unit.y - 8, unit.width, 4);
                ctx.fillStyle = "#4caf50";
                ctx.fillRect(unit.x, unit.y - 8, unit.width * (unit.hp / unit.maxHp), 4);
            });

            enemyUnits.forEach(unit => {
                ctx.fillStyle = unit.color;
                ctx.fillRect(unit.x, unit.y, unit.width, unit.height);
                ctx.strokeStyle = '#000000';
                ctx.lineWidth = 2;
                ctx.strokeRect(unit.x, unit.y, unit.width, unit.height);

                if (unit.isBoss) {
                    ctx.fillStyle = "#d81b60";
                    const mouthOpen = (unit.atkTimer % 10 > 5) ? 12 : 4;
                    ctx.fillRect(unit.x + unit.width - 5, unit.y + 15, 10, mouthOpen);
                    ctx.strokeRect(unit.x + unit.width - 5, unit.y + 15, 10, mouthOpen);
                }

                ctx.fillStyle = "#ff5252";
                ctx.fillRect(unit.x, unit.y - 8, unit.width, 4);
                ctx.fillStyle = "#4caf50";
                ctx.fillRect(unit.x, unit.y - 8, unit.width * (unit.hp / unit.maxHp), 4);
            });

            if (waveEffect.active) {
                ctx.save();
                ctx.strokeStyle = "rgba(239, 83, 80, 0.7)";
                ctx.lineWidth = 6;
                ctx.beginPath();
                ctx.arc(enemyCastle.x + enemyCastle.width, groundY - 40, waveEffect.radius, 0, Math.PI * 2);
                ctx.stroke();
                ctx.restore();
            }
        }

        function gameLoop() {
            update();
            render();
            requestAnimationFrame(gameLoop);
        }

        gameLoop();
    </script>
</body>
</html>
"""

components.html(game_code, height=540)
