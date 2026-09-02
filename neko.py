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
        .settings-btn:hover { background-color: #455a64; }
        .money-display { font-size: 18px; font-weight: bold; color: #2e7d32; }
        .stage-title { font-size: 18px; font-weight: bold; color: #1565c0; }

        /* 화면 오버레이 공통 (홈, 스테이지 선택, 덱편성 등) */
        .screen-overlay {
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
            background-color: rgba(0, 0, 0, 0.5);
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
            margin: 5px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            min-width: 160px;
        }
        .action-btn:hover { background-color: #f57c00; }
        .action-btn.disabled { background-color: #b0bec5; border-color: #78909c; cursor: not-allowed; }

        /* 하단 8칸 덱 컨트롤 (4x2) */
        .controls-container {
            display: flex;
            flex-direction: column;
            gap: 6px;
            margin-top: 5px;
            align-items: center;
            width: 800px;
        }
        .controls-row {
            display: flex;
            gap: 10px;
        }
        .unit-slot {
            position: relative;
            width: 70px;
            height: 55px;
            background-color: #ffffff;
            border: 2px solid #333;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-size: 11px;
            font-weight: bold;
            user-select: none;
            overflow: hidden;
            box-sizing: border-box;
        }
        .unit-slot.disabled { cursor: not-allowed; background-color: #e0e0e0; color: #888; }
        .unit-slot.empty { background-color: #eceff1; border: 2px dashed #b0bec5; cursor: default; color: #b0bec5; }
        
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
        .cost-tag { font-size: 10px; color: #d32f2f; margin-top: 2px; }

        /* 팝업 모달 */
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
            z-index: 30;
            box-sizing: border-box;
        }
        
        /* 덱 편성 UI 전용 */
        .deck-builder-box {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 10px;
        }
        .inventory-list {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
        .inv-item {
            padding: 8px 12px;
            background: #fff;
            border: 2px solid #333;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            font-weight: bold;
        }
        .inv-item.selected { opacity: 0.4; cursor: default; }
    </style>
</head>
<body>
    <div class="top-bar">
        <div class="left-group">
            <button class="settings-btn" onclick="openSettings()">⚙️ 설정</button>
            <div class="money-display">💰 소지금: <span id="moneyTxt">0</span>원 / 1000원</div>
        </div>
        <div class="stage-title" id="stageTxt">🚩 대기 중</div>
    </div>

    <div class="game-container">
        <canvas id="gameCanvas" width="800" height="300"></canvas>
        
        <!-- 홈 화면 -->
        <div id="homeScreen" class="screen-overlay" style="display: flex;">
            <h1 style="margin-bottom: 20px;">🐱 미니 냥코대전쟁</h1>
            <div style="display: flex; gap: 15px;">
                <button class="action-btn" onclick="openStageSelect()">⚔️ 전투개시</button>
                <button class="action-btn" onclick="openDeckBuilder()" style="background-color: #2196f3; border-color: #0b7dda;">🎴 덱 편성</button>
                <button class="action-btn" onclick="openGachaNotice()" style="background-color: #9c27b0; border-color: #7b1fa2;">🎰 뽑기</button>
            </div>
        </div>

        <!-- 스테이지 선택 화면 -->
        <div id="stageSelectScreen" class="screen-overlay">
            <h2>🚩 스테이지 선택</h2>
            <div style="display: flex; gap: 15px; margin: 15px 0;" id="stageBtnList">
                <!-- 자바스크립트로 동적 생성 -->
            </div>
            <button class="action-btn" onclick="showHomeScreen()" style="background-color: #607d8b; border-color: #455a64;">🏠 홈으로</button>
        </div>

        <!-- 덱 편성 화면 -->
        <div id="deckScreen" class="screen-overlay">
            <h3>🎴 덱 편성 (8칸)</h3>
            <p style="font-size: 12px; color: #666; margin: 0 0 10px 0;">덱 슬롯 클릭 시 제거 / 하단 캐릭터 클릭 시 비어있는 슬롯에 추가</p>
            <div class="deck-builder-box">
                <div id="deckPreviewRow1" class="controls-row"></div>
                <div id="deckPreviewRow2" class="controls-row"></div>
                <div style="font-weight: bold; margin-top: 5px; font-size: 13px;">[ 보유 캐릭터 목록 ]</div>
                <div class="inventory-list" id="inventoryList"></div>
            </div>
            <button class="action-btn" onclick="showHomeScreen()" style="background-color: #4caf50; border-color: #2e7d32; margin-top: 10px;">💾 저장 및 홈으로</button>
        </div>

        <!-- 중앙 오버레이 (승리/패배/시작) -->
        <div id="centerOverlay" class="center-overlay" style="display: none;">
            <h2 id="overlayMsg" style="color: white; margin: 0 0 10px 0; font-size: 26px;"></h2>
            <button id="btnRewardNext" class="action-btn" style="display: none;" onclick="handleVictoryComplete()">🎁 보상 확인 및 홈으로</button>
            <button id="btnDefeatHome" class="action-btn" style="display: none; background-color: #607d8b;" onclick="showHomeScreen()">🏠 홈으로 돌아가기</button>
        </div>

        <!-- 설정 모달 -->
        <div id="settingsModal" class="modal">
            <h2>⚙️ 설정</h2>
            <div style="margin: 15px 0;">
                <label for="volumeRange"><b>🔊 소리 조절</b></label><br><br>
                <input type="range" id="volumeRange" min="0" max="1" step="0.05" value="0.3" oninput="changeVolume(this.value)">
            </div>
            <div style="display: flex; flex-direction: column; gap: 8px;">
                <button class="action-btn" style="background-color: #4caf50; width: 100%; margin: 0;" onclick="closeSettings()">▶️ 계속하기</button>
                <button class="action-btn" style="background-color: #2196f3; width: 100%; margin: 0;" onclick="goToHomeFromSettings()">🏠 홈으로</button>
            </div>
        </div>

        <!-- 캐릭터 획득 팝업 창 -->
        <div id="rewardModal" class="modal">
            <h2>🎉 캐릭터 해금!</h2>
            <p id="rewardText"><b>[🪓 도끼맨]</b>을(를) 획득했습니다!</p>
            <button class="action-btn" style="background-color: #4caf50; border-color: #2e7d32; width: 100%; margin: 0;" onclick="closeRewardAndGoHome()">🏠 홈으로 이동</button>
        </div>
    </div>

    <!-- 하단 덱 컨트롤 (4x2 슬롯) -->
    <div class="controls-container">
        <div class="controls-row" id="battleRow1"></div>
        <div class="controls-row" id="battleRow2"></div>
    </div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");
        const groundY = 220;

        let currentStage = 1;
        let maxUnlockedStage = 1; // 해금된 최고 스테이지
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
            if (masterGain) masterGain.gain.value = masterVolume;
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
            const notes = [261.63, 329.63, 392.00, 523.25];
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

        // 캐릭터 DB
        const characterDB = {
            basic: { name: "🐱 기본", cost: 50,  cooldown: 500,  hp: 30, atk: 10, speed: 1.2, width: 25, height: 25, range: 5,   color: '#ffffff', atkCooldown: 60 },
            tank:  { name: "🦒 탱커", cost: 75,  cooldown: 1000, hp: 60, atk: 7,  speed: 0.6, width: 20, height: 50, range: 5,   color: '#ffffff', atkCooldown: 80 },
            axe:   { name: "🪓 도끼맨", cost: 100, cooldown: 2000, hp: 20, atk: 25, speed: 1.0, width: 25, height: 30, range: 125, color: '#ff7043', atkCooldown: 70 }
        };

        let unlockedCharacters = ['basic', 'tank']; // 보유한 캐릭터 목록
        let currentDeck = ['basic', 'tank', null, null, null, null, null, null]; // 8칸 덱

        const enemyUnitConfigs = {
            doge:  { hp: 20,  atk: 8,  speed: 0.9, width: 25, height: 25, color: '#ffcc80', atkCooldown: 60 },
            snake: { hp: 17,  atk: 11, speed: 1.4, width: 35, height: 15, color: '#a5d6a7', atkCooldown: 50 },
            hippo: { hp: 300, atk: 20, speed: 0.5, width: 50, height: 40, color: '#f8bbd0', atkCooldown: 45 }
        };

        const cooldownState = Array(8).fill(null).map(() => ({ ready: true, remaining: 0, total: 1000 }));

        let playerCastle = { x: 690, y: groundY - 80, width: 60, height: 80, hp: 200, maxHp: 200 };
        let enemyCastle = { x: 50, y: groundY - 80, width: 60, height: 80, hp: 200, maxHp: 200 };

        let playerUnits = [];
        let enemyUnits = [];

        let lastEnemySpawnTime = Date.now();
        let bossSpawned = false;
        let waveEffect = { active: false, radius: 0, maxRadius: 300 };

        // 홈/화면 전환 로직
        function hideAllScreens() {
            document.getElementById("homeScreen").style.display = "none";
            document.getElementById("stageSelectScreen").style.display = "none";
            document.getElementById("deckScreen").style.display = "none";
            document.getElementById("centerOverlay").style.display = "none";
            document.getElementById("settingsModal").style.display = "none";
            document.getElementById("rewardModal").style.display = "none";
        }

        function showHomeScreen() {
            hideAllScreens();
            gameStarted = false;
            isPaused = true;
            document.getElementById("homeScreen").style.display = "flex";
            document.getElementById("stageTxt").innerText = "🚩 대기 중";
            renderBattleDeckSlots();
        }

        function openStageSelect() {
            hideAllScreens();
            const container = document.getElementById("stageBtnList");
            container.innerHTML = "";
            for (let i = 1; i <= 2; i++) {
                const btn = document.createElement("button");
                btn.className = "action-btn" + (i <= maxUnlockedStage ? "" : " disabled");
                btn.innerText = "Stage " + i + (i <= maxUnlockedStage ? " ⚔️" : " 🔒");
                if (i <= maxUnlockedStage) {
                    btn.onclick = () => startBattleStage(i);
                }
                container.appendChild(btn);
            }
            document.getElementById("stageSelectScreen").style.display = "flex";
        }

        function openDeckBuilder() {
            hideAllScreens();
            renderDeckBuilder();
            document.getElementById("deckScreen").style.display = "flex";
        }

        function openGachaNotice() {
            alert("🎰 뽑기 기능은 준비 중입니다!");
        }

        // 덱 편성 UI 처리
        function renderDeckBuilder() {
            const row1 = document.getElementById("deckPreviewRow1");
            const row2 = document.getElementById("deckPreviewRow2");
            row1.innerHTML = ""; row2.innerHTML = "";

            for (let i = 0; i < 8; i++) {
                const charKey = currentDeck[i];
                const slot = document.createElement("div");
                slot.className = "unit-slot" + (charKey ? "" : " empty");
                if (charKey) {
                    slot.innerHTML = `<div>${characterDB[charKey].name}</div><div class="cost-tag">${characterDB[charKey].cost}원</div>`;
                    slot.onclick = () => removeFromDeck(i);
                } else {
                    slot.innerText = "EMPTY";
                }
                if (i < 4) row1.appendChild(slot);
                else row2.appendChild(slot);
            }

            const invList = document.getElementById("inventoryList");
            invList.innerHTML = "";
            unlockedCharacters.forEach(key => {
                const inUse = currentDeck.includes(key);
                const item = document.createElement("div");
                item.className = "inv-item" + (inUse ? " selected" : "");
                item.innerText = characterDB[key].name;
                if (!inUse) item.onclick = () => addToDeck(key);
                invList.appendChild(item);
            });
        }

        function addToDeck(charKey) {
            const emptyIdx = currentDeck.indexOf(null);
            if (emptyIdx !== -1) {
                currentDeck[emptyIdx] = charKey;
                renderDeckBuilder();
            } else {
                alert("덱이 가득 찼습니다! (최대 8개)");
            }
        }

        function removeFromDeck(index) {
            currentDeck[index] = null;
            renderDeckBuilder();
        }

        // 전투 하단 UI 레이아웃 동적 생성 (4x2)
        function renderBattleDeckSlots() {
            const row1 = document.getElementById("battleRow1");
            const row2 = document.getElementById("battleRow2");
            row1.innerHTML = ""; row2.innerHTML = "";

            for (let i = 0; i < 8; i++) {
                const charKey = currentDeck[i];
                const slot = document.createElement("div");
                slot.id = "bSlot_" + i;
                if (charKey) {
                    const cfg = characterDB[charKey];
                    slot.className = "unit-slot disabled";
                    slot.innerHTML = `<div>${cfg.name}</div><div class="cost-tag">${cfg.cost}원</div><div id="cd_${i}" class="cooldown-overlay" style="height: 0%;"></div>`;
                    slot.onclick = () => spawnPlayerUnit(i);
                } else {
                    slot.className = "unit-slot empty";
                    slot.innerText = "EMPTY";
                }
                if (i < 4) row1.appendChild(slot);
                else row2.appendChild(slot);
            }
        }

        function startBattleStage(stageNum) {
            initAudio();
            hideAllScreens();
            currentStage = stageNum;
            gameStarted = true;
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
            lastEnemySpawnTime = Date.now();
            renderBattleDeckSlots();
        }

        function triggerCooldown(index, duration) {
            cooldownState[index].ready = false;
            cooldownState[index].total = duration;
            cooldownState[index].remaining = duration;

            const interval = 20;
            const timer = setInterval(() => {
                if (!isPaused) {
                    cooldownState[index].remaining -= interval;
                    if (cooldownState[index].remaining <= 0) {
                        cooldownState[index].remaining = 0;
                        cooldownState[index].ready = true;
                        clearInterval(timer);
                    }
                }
            }, interval);
        }

        function spawnPlayerUnit(slotIndex) {
            if (!gameStarted || gameOver || isPaused) return;
            const charKey = currentDeck[slotIndex];
            if (!charKey) return;

            const config = characterDB[charKey];
            if (money < config.cost || !cooldownState[slotIndex].ready) return;

            money -= config.cost;
            playSpawnSound();
            triggerCooldown(slotIndex, config.cooldown);

            playerUnits.push({
                type: charKey,
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

        function openSettings() {
            initAudio();
            isPaused = true;
            document.getElementById("settingsModal").style.display = "block";
        }

        function closeSettings() {
            isPaused = false;
            document.getElementById("settingsModal").style.display = "none";
        }

        function goToHomeFromSettings() {
            showHomeScreen();
        }

        function handleVictoryComplete() {
            document.getElementById("centerOverlay").style.display = "none";
            if (currentStage === 1 && !unlockedCharacters.includes('axe')) {
                unlockedCharacters.push('axe');
                maxUnlockedStage = Math.max(maxUnlockedStage, 2);
                document.getElementById("rewardModal").style.display = "block";
            } else {
                showHomeScreen();
            }
        }

        function closeRewardAndGoHome() {
            document.getElementById("rewardModal").style.display = "none";
            showHomeScreen();
        }

        function updateUI() {
            document.getElementById("moneyTxt").innerText = Math.floor(money);

            for (let i = 0; i < 8; i++) {
                const charKey = currentDeck[i];
                if (!charKey) continue;

                const slot = document.getElementById("bSlot_" + i);
                const cdElem = document.getElementById("cd_" + i);
                if (slot && cdElem) {
                    cdElem.style.height = ((cooldownState[i].remaining / cooldownState[i].total) * 100) + "%";
                    if (gameStarted && !gameOver && !isPaused && money >= characterDB[charKey].cost && cooldownState[i].ready) {
                        slot.classList.remove("disabled");
                    } else {
                        slot.classList.add("disabled");
                    }
                }
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
                if (waveEffect.radius >= waveEffect.maxRadius) waveEffect.active = false;
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
                document.getElementById("overlayMsg").innerText = "🎉 VICTORY (승리!)";
                document.getElementById("btnRewardNext").style.display = "inline-block";
                document.getElementById("btnDefeatHome").style.display = "none";
            } else if (playerCastle.hp <= 0) {
                gameOver = true;
                gameWon = false;
                document.getElementById("centerOverlay").style.display = "flex";
                document.getElementById("overlayMsg").innerText = "💀 DEFEAT (패배)";
                document.getElementById("btnRewardNext").style.display = "none";
                document.getElementById("btnDefeatHome").style.display = "inline-block";
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

        showHomeScreen();
        gameLoop();
    </script>
</body>
</html>
"""

components.html(game_code, height=580)
