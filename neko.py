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
        canvas {
            border: 2px solid #333;
            background-color: #e0f7fa;
        }
        .top-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 800px;
            margin: 10px 0;
        }
        .money-display {
            font-size: 18px;
            font-weight: bold;
            color: #2e7d32;
        }
        .start-btn {
            padding: 8px 20px;
            font-size: 15px;
            font-weight: bold;
            color: #fff;
            background-color: #ff9800;
            border: 2px solid #e65100;
            border-radius: 6px;
            cursor: pointer;
        }
        .start-btn:disabled {
            background-color: #bbb;
            border-color: #888;
            cursor: not-allowed;
        }

        /* 4칸 정사각형 슬롯 레이아웃 */
        .controls {
            display: flex;
            gap: 12px;
            margin-top: 5px;
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
        
        /* 쿨타임 오버레이 연출 */
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
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="800" height="300"></canvas>
    
    <div class="top-bar">
        <div class="money-display">💰 소지금: <span id="moneyTxt">0</span>원 / 1000원</div>
        <button id="btnStart" class="start-btn" onclick="startGame()">⚔️ 게임 시작</button>
    </div>

    <div class="controls">
        <!-- Slot 1: 기본 고양이 -->
        <div id="slotBasic" class="unit-slot disabled" onclick="spawnPlayerUnit('basic')">
            <div>🐱 기본</div>
            <div class="cost-tag">50원</div>
            <div id="cdBasic" class="cooldown-overlay" style="height: 0%;"></div>
        </div>

        <!-- Slot 2: 탱커 고양이 -->
        <div id="slotTank" class="unit-slot disabled" onclick="spawnPlayerUnit('tank')">
            <div>🦒 탱커</div>
            <div class="cost-tag">75원</div>
            <div id="cdTank" class="cooldown-overlay" style="height: 0%;"></div>
        </div>

        <!-- Slot 3: 빈 슬롯 -->
        <div class="unit-slot empty">
            <div>EMPTY</div>
        </div>

        <!-- Slot 4: 빈 슬롯 -->
        <div class="unit-slot empty">
            <div>EMPTY</div>
        </div>
    </div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        const groundY = 220;

        let gameStarted = false;
        let gameOver = false;

        let money = 0;
        const maxMoney = 1000;
        const moneyIncomeRate = 0.5;

        const playerUnitConfigs = {
            basic: { cost: 50, cooldown: 500, hp: 30, atk: 10, speed: 1.2, width: 25, height: 25, color: '#ffffff', atkCooldown: 60 },
            tank:  { cost: 75, cooldown: 1000, hp: 60, atk: 7,  speed: 0.6, width: 20, height: 50, color: '#ffffff', atkCooldown: 80 }
        };

        const enemyUnitConfigs = {
            doge: { hp: 20, atk: 8,  speed: 0.9, width: 25, height: 25, color: '#ffcc80', atkCooldown: 60 },
            snake:{ hp: 17, atk: 11, speed: 1.4, width: 35, height: 15, color: '#a5d6a7', atkCooldown: 50 }
        };

        // 쿨타임 타이머 관리
        const cooldownState = {
            basic: { ready: true, remaining: 0, total: 500 },
            tank:  { ready: true, remaining: 0, total: 1000 }
        };

        const playerCastle = { x: 50, y: groundY - 80, width: 60, height: 80, hp: 200, maxHp: 200 };
        const enemyCastle = { x: 690, y: groundY - 80, width: 60, height: 80, hp: 200, maxHp: 200 };

        const playerUnits = [];
        const enemyUnits = [];

        let lastEnemySpawnTime = Date.now();

        function startGame() {
            if (gameStarted) return;
            gameStarted = true;
            document.getElementById("btnStart").disabled = true;
            document.getElementById("btnStart").innerText = "게임 진행 중";
            lastEnemySpawnTime = Date.now();
        }

        function triggerCooldown(type) {
            const config = playerUnitConfigs[type];
            cooldownState[type].ready = false;
            cooldownState[type].total = config.cooldown;
            cooldownState[type].remaining = config.cooldown;

            const interval = 20;
            const timer = setInterval(() => {
                cooldownState[type].remaining -= interval;
                if (cooldownState[type].remaining <= 0) {
                    cooldownState[type].remaining = 0;
                    cooldownState[type].ready = true;
                    clearInterval(timer);
                }
            }, interval);
        }

        function spawnPlayerUnit(type) {
            if (!gameStarted || gameOver) return;
            const config = playerUnitConfigs[type];

            if (money < config.cost || !cooldownState[type].ready) return;

            money -= config.cost;
            triggerCooldown(type);

            playerUnits.push({
                x: playerCastle.x + playerCastle.width,
                y: groundY - config.height,
                width: config.width,
                height: config.height,
                speed: config.speed,
                hp: config.hp,
                maxHp: config.hp,
                atk: config.atk,
                color: config.color,
                atkTimer: 0,
                atkCooldown: config.atkCooldown
            });
        }

        function spawnEnemyUnit() {
            if (!gameStarted || gameOver) return;
            const now = Date.now();
            if (now - lastEnemySpawnTime > Math.random() * 1500 + 2500) {
                lastEnemySpawnTime = now;

                const spawnCount = Math.random() < 0.2 ? 2 : 1;
                for (let i = 0; i < spawnCount; i++) {
                    const isDoge = Math.random() < 0.6;
                    const config = isDoge ? enemyUnitConfigs.doge : enemyUnitConfigs.snake;

                    enemyUnits.push({
                        x: enemyCastle.x - config.width - (i * 20),
                        y: groundY - config.height,
                        width: config.width,
                        height: config.height,
                        speed: config.speed,
                        hp: config.hp,
                        maxHp: config.hp,
                        atk: config.atk,
                        color: config.color,
                        atkTimer: 0,
                        atkCooldown: config.atkCooldown
                    });
                }
            }
        }

        function updateUI() {
            document.getElementById("moneyTxt").innerText = Math.floor(money);

            // 기본 고양이 슬롯 상태
            const slotBasic = document.getElementById("slotBasic");
            const cdBasic = document.getElementById("cdBasic");
            const basicRatio = cooldownState.basic.remaining / cooldownState.basic.total;
            cdBasic.style.height = (basicRatio * 100) + "%";

            if (gameStarted && !gameOver && money >= playerUnitConfigs.basic.cost && cooldownState.basic.ready) {
                slotBasic.classList.remove("disabled");
            } else {
                slotBasic.classList.add("disabled");
            }

            // 탱커 고양이 슬롯 상태
            const slotTank = document.getElementById("slotTank");
            const cdTank = document.getElementById("cdTank");
            const tankRatio = cooldownState.tank.remaining / cooldownState.tank.total;
            cdTank.style.height = (tankRatio * 100) + "%";

            if (gameStarted && !gameOver && money >= playerUnitConfigs.tank.cost && cooldownState.tank.ready) {
                slotTank.classList.remove("disabled");
            } else {
                slotTank.classList.add("disabled");
            }
        }

        function update() {
            if (!gameStarted || gameOver) {
                updateUI();
                return;
            }

            if (money < maxMoney) {
                money = Math.min(maxMoney, money + moneyIncomeRate);
            }

            spawnEnemyUnit();

            playerUnits.forEach((pUnit) => {
                let targetEnemy = null;
                for (let eUnit of enemyUnits) {
                    if (eUnit.x > pUnit.x && eUnit.x <= pUnit.x + pUnit.width + 5) {
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
                } else if (pUnit.x + pUnit.width >= enemyCastle.x) {
                    pUnit.atkTimer++;
                    if (pUnit.atkTimer >= pUnit.atkCooldown) {
                        pUnit.atkTimer = 0;
                        enemyCastle.hp = Math.max(0, enemyCastle.hp - pUnit.atk);
                    }
                } else {
                    pUnit.x += pUnit.speed;
                }
            });

            enemyUnits.forEach((eUnit) => {
                let targetPlayer = null;
                for (let pUnit of playerUnits) {
                    if (pUnit.x + pUnit.width >= eUnit.x - 5 && pUnit.x < eUnit.x) {
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
                } else if (eUnit.x <= playerCastle.x + playerCastle.width) {
                    eUnit.atkTimer++;
                    if (eUnit.atkTimer >= eUnit.atkCooldown) {
                        eUnit.atkTimer = 0;
                        playerCastle.hp = Math.max(0, playerCastle.hp - eUnit.atk);
                    }
                } else {
                    eUnit.x -= eUnit.speed;
                }
            });

            for (let i = playerUnits.length - 1; i >= 0; i--) {
                if (playerUnits[i].hp <= 0) playerUnits.splice(i, 1);
            }
            for (let i = enemyUnits.length - 1; i >= 0; i--) {
                if (enemyUnits[i].hp <= 0) enemyUnits.splice(i, 1);
            }

            if (playerCastle.hp <= 0 || enemyCastle.hp <= 0) {
                gameOver = true;
            }

            updateUI();
        }

        function render() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 바닥
            ctx.fillStyle = "#81c784";
            ctx.fillRect(0, groundY, canvas.width, canvas.height - groundY);
            ctx.strokeStyle = "#388e3c";
            ctx.lineWidth = 4;
            ctx.beginPath();
            ctx.moveTo(0, groundY);
            ctx.lineTo(canvas.width, groundY);
            ctx.stroke();

            // 아군 성
            ctx.fillStyle = "#42a5f5";
            ctx.fillRect(playerCastle.x, playerCastle.y, playerCastle.width, playerCastle.height);
            ctx.fillStyle = "#1e88e5";
            ctx.beginPath();
            ctx.moveTo(playerCastle.x - 10, playerCastle.y);
            ctx.lineTo(playerCastle.x + playerCastle.width / 2, playerCastle.y - 30);
            ctx.lineTo(playerCastle.x + playerCastle.width + 10, playerCastle.y);
            ctx.closePath();
            ctx.fill();

            // 적군 성
            ctx.fillStyle = "#ef5350";
            ctx.fillRect(enemyCastle.x, enemyCastle.y, enemyCastle.width, enemyCastle.height);
            ctx.fillStyle = "#e53935";
            ctx.beginPath();
            ctx.moveTo(enemyCastle.x - 10, enemyCastle.y);
            ctx.lineTo(enemyCastle.x + enemyCastle.width / 2, enemyCastle.y - 30);
            ctx.lineTo(enemyCastle.x + enemyCastle.width + 10, enemyCastle.y);
            ctx.closePath();
            ctx.fill();

            // 성 이름
            ctx.fillStyle = "#000000";
            ctx.font = "bold 13px sans-serif";
            ctx.textAlign = "center";
            ctx.fillText("아군 성 (" + playerCastle.hp + "/" + playerCastle.maxHp + ")", playerCastle.x + playerCastle.width / 2, playerCastle.y - 40);
            ctx.fillText("적군 성 (" + enemyCastle.hp + "/" + enemyCastle.maxHp + ")", enemyCastle.x + enemyCastle.width / 2, enemyCastle.y - 40);

            // 성 체력바
            ctx.fillStyle = "#e0e0e0";
            ctx.fillRect(playerCastle.x, playerCastle.y - 35, playerCastle.width, 6);
            ctx.fillRect(enemyCastle.x, enemyCastle.y - 35, enemyCastle.width, 6);
            
            ctx.fillStyle = "#4caf50";
            ctx.fillRect(playerCastle.x, playerCastle.y - 35, playerCastle.width * (playerCastle.hp / playerCastle.maxHp), 6);
            ctx.fillRect(enemyCastle.x, enemyCastle.y - 35, enemyCastle.width * (enemyCastle.hp / enemyCastle.maxHp), 6);

            // 아군 유닛
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

                ctx.fillStyle = "#ff5252";
                ctx.fillRect(unit.x, unit.y - 8, unit.width, 4);
                ctx.fillStyle = "#4caf50";
                ctx.fillRect(unit.x, unit.y - 8, unit.width * (unit.hp / unit.maxHp), 4);
            });

            // 적군 유닛
            enemyUnits.forEach(unit => {
                ctx.fillStyle = unit.color;
                ctx.fillRect(unit.x, unit.y, unit.width, unit.height);
                ctx.strokeStyle = '#000000';
                ctx.lineWidth = 2;
                ctx.strokeRect(unit.x, unit.y, unit.width, unit.height);

                ctx.fillStyle = "#ff5252";
                ctx.fillRect(unit.x, unit.y - 8, unit.width, 4);
                ctx.fillStyle = "#4caf50";
                ctx.fillRect(unit.x, unit.y - 8, unit.width * (unit.hp / unit.maxHp), 4);
            });

            // 안내 문구 (시작 전)
            if (!gameStarted) {
                ctx.fillStyle = "rgba(0, 0, 0, 0.4)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 24px sans-serif";
                ctx.textAlign = "center";
                ctx.fillText("⚔️ 상단의 [게임 시작] 버튼을 눌러주세요!", canvas.width / 2, canvas.height / 2);
            }

            // 게임 오버
            if (gameOver) {
                ctx.fillStyle = "rgba(0, 0, 0, 0.6)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 32px sans-serif";
                ctx.textAlign = "center";
                if (enemyCastle.hp <= 0) {
                    ctx.fillText("🎉 VICTORY! (승리)", canvas.width / 2, canvas.height / 2);
                } else {
                    ctx.fillText("💀 DEFEAT... (패배)", canvas.width / 2, canvas.height / 2);
                }
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

components.html(game_code, height=480)
