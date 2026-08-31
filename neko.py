import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="미니 냥코대전쟁", layout="centered")
st.title("🐱 미니 냥코대전쟁")

game_code = """
<!DOCTYPE html>
<html>
<head>
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
        .money-display {
            font-size: 18px;
            font-weight: bold;
            margin: 10px 0 5px 0;
            color: #2e7d32;
        }
        .controls {
            display: flex;
            gap: 12px;
        }
        button {
            padding: 10px 16px;
            font-size: 13px;
            font-weight: bold;
            cursor: pointer;
            border: 2px solid #333;
            border-radius: 6px;
            background-color: #ffffff;
            transition: background-color 0.1s;
        }
        button:disabled {
            background-color: #ccc;
            cursor: not-allowed;
            color: #666;
            border-color: #999;
        }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="800" height="300"></canvas>
    
    <div class="money-display">💰 소지금: <span id="moneyTxt">0</span>원 / 1000원</div>

    <div class="controls">
        <button id="btnBasic" onclick="spawnPlayerUnit('basic')">🐱 기본 (50원)</button>
        <button id="btnTank" onclick="spawnPlayerUnit('tank')">🦒 탱커 (75원)</button>
    </div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        const groundY = 220;

        // 재화(돈) 및 쿨타임 시스템 데이터
        let money = 0;
        const maxMoney = 1000;
        const moneyIncomeRate = 0.5;

        // 유닛 설정
        const playerUnitConfigs = {
            basic: { cost: 50, cooldown: 500, hp: 30, atk: 10, speed: 1.2, width: 25, height: 25, color: '#ffffff', atkCooldown: 60 },
            tank:  { cost: 75, cooldown: 1000, hp: 60, atk: 7,  speed: 0.6, width: 20, height: 50, color: '#ffffff', atkCooldown: 80 }
        };

        const enemyUnitConfigs = {
            doge: { hp: 20, atk: 8,  speed: 0.9, width: 25, height: 25, color: '#ffcc80', atkCooldown: 60 }, // 기본 멍뭉이 (주황/갈색계열)
            snake:{ hp: 17, atk: 11, speed: 1.4, width: 35, height: 15, color: '#a5d6a7', atkCooldown: 50 }  # 뱀 (초록색 계열)
        };

        const cooldownState = {
            basic: { ready: true },
            tank:  { ready: true }
        };

        // 성 설정 (HP: 200)
        const playerCastle = { x: 50, y: groundY - 80, width: 60, height: 80, hp: 200, maxHp: 200 };
        const enemyCastle = { x: 690, y: groundY - 80, width: 60, height: 80, hp: 200, maxHp: 200 };

        // 유닛 배열
        const playerUnits = [];
        const enemyUnits = [];

        // 적 생성 관련 타임스탬프
        let lastEnemySpawnTime = Date.now();
        let gameOver = false;

        // 아군 유닛 소환
        function spawnPlayerUnit(type) {
            if (gameOver) return;
            const config = playerUnitConfigs[type];

            if (money < config.cost || !cooldownState[type].ready) return;

            money -= config.cost;

            cooldownState[type].ready = false;
            setTimeout(() => {
                cooldownState[type].ready = true;
            }, config.cooldown);

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
                atkCooldown: config.atkCooldown,
                type: type
            });
        }

        // 적 유닛 자동 소환
        function spawnEnemyUnit() {
            if (gameOver) return;
            const now = Date.now();
            // 2.5초~4초 간격으로 랜덤 소환
            if (now - lastEnemySpawnTime > Math.random() * 1500 + 2500) {
                lastEnemySpawnTime = now;

                // 60% 확률로 멍뭉이, 40% 확률로 뱀 생성 (가끔 연속 소환)
                const spawnCount = Math.random() < 0.2 ? 2 : 1; // 20% 확률로 2마리 다중 소환
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
                        atkCooldown: config.atkCooldown,
                        type: isDoge ? 'doge' : 'snake'
                    });
                }
            }
        }

        function updateUI() {
            document.getElementById("moneyTxt").innerText = Math.floor(money);

            const btnBasic = document.getElementById("btnBasic");
            const btnTank = document.getElementById("btnTank");

            btnBasic.disabled = gameOver || (money < playerUnitConfigs.basic.cost) || !cooldownState.basic.ready;
            btnTank.disabled = gameOver || (money < playerUnitConfigs.tank.cost) || !cooldownState.tank.ready;
        }

        function update() {
            if (gameOver) return;

            // 돈 수급
            if (money < maxMoney) {
                money = Math.min(maxMoney, money + moneyIncomeRate);
            }

            // 적 자동 생성 체크
            spawnEnemyUnit();

            // --- 아군 유닛 로직 ---
            playerUnits.forEach((pUnit) => {
                // 가장 가까운 적 찾기
                let targetEnemy = null;
                for (let eUnit of enemyUnits) {
                    if (eUnit.x > pUnit.x && eUnit.x <= pUnit.x + pUnit.width + 5) {
                        targetEnemy = eUnit;
                        break;
                    }
                }

                if (targetEnemy) {
                    // 적 공격
                    pUnit.atkTimer++;
                    if (pUnit.atkTimer >= pUnit.atkCooldown) {
                        pUnit.atkTimer = 0;
                        targetEnemy.hp -= pUnit.atk;
                    }
                } else if (pUnit.x + pUnit.width >= enemyCastle.x) {
                    // 적 성 공격
                    pUnit.atkTimer++;
                    if (pUnit.atkTimer >= pUnit.atkCooldown) {
                        pUnit.atkTimer = 0;
                        enemyCastle.hp = Math.max(0, enemyCastle.hp - pUnit.atk);
                    }
                } else {
                    // 전진
                    pUnit.x += pUnit.speed;
                }
            });

            // --- 적군 유닛 로직 ---
            enemyUnits.forEach((eUnit) => {
                // 가장 가까운 아군 찾기
                let targetPlayer = null;
                for (let pUnit of playerUnits) {
                    if (pUnit.x + pUnit.width >= eUnit.x - 5 && pUnit.x < eUnit.x) {
                        targetPlayer = pUnit;
                        break;
                    }
                }

                if (targetPlayer) {
                    // 아군 공격
                    eUnit.atkTimer++;
                    if (eUnit.atkTimer >= eUnit.atkCooldown) {
                        eUnit.atkTimer = 0;
                        targetPlayer.hp -= eUnit.atk;
                    }
                } else if (eUnit.x <= playerCastle.x + playerCastle.width) {
                    // 아군 성 공격
                    eUnit.atkTimer++;
                    if (eUnit.atkTimer >= eUnit.atkCooldown) {
                        eUnit.atkTimer = 0;
                        playerCastle.hp = Math.max(0, playerCastle.hp - eUnit.atk);
                    }
                } else {
                    // 전진
                    eUnit.x -= eUnit.speed;
                }
            });

            // 체력이 0 이하인 유닛 제거
            for (let i = playerUnits.length - 1; i >= 0; i--) {
                if (playerUnits[i].hp <= 0) playerUnits.splice(i, 1);
            }
            for (let i = enemyUnits.length - 1; i >= 0; i--) {
                if (enemyUnits[i].hp <= 0) enemyUnits.splice(i, 1);
            }

            // 게임 승패 판정
            if (playerCastle.hp <= 0 || enemyCastle.hp <= 0) {
                gameOver = true;
            }

            updateUI();
        }

        function render() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 1. 바닥
            ctx.fillStyle = "#81c784";
            ctx.fillRect(0, groundY, canvas.width, canvas.height - groundY);
            
            ctx.strokeStyle = "#388e3c";
            ctx.lineWidth = 4;
            ctx.beginPath();
            ctx.moveTo(0, groundY);
            ctx.lineTo(canvas.width, groundY);
            ctx.stroke();

            // 2. 아군 성
            ctx.fillStyle = "#42a5f5";
            ctx.fillRect(playerCastle.x, playerCastle.y, playerCastle.width, playerCastle.height);
            ctx.fillStyle = "#1e88e5";
            ctx.beginPath();
            ctx.moveTo(playerCastle.x - 10, playerCastle.y);
            ctx.lineTo(playerCastle.x + playerCastle.width / 2, playerCastle.y - 30);
            ctx.lineTo(playerCastle.x + playerCastle.width + 10, playerCastle.y);
            ctx.closePath();
            ctx.fill();

            // 3. 적군 성
            ctx.fillStyle = "#ef5350";
            ctx.fillRect(enemyCastle.x, enemyCastle.y, enemyCastle.width, enemyCastle.height);
            ctx.fillStyle = "#e53935";
            ctx.beginPath();
            ctx.moveTo(enemyCastle.x - 10, enemyCastle.y);
            ctx.lineTo(enemyCastle.x + enemyCastle.width / 2, enemyCastle.y - 30);
            ctx.lineTo(enemyCastle.x + enemyCastle.width + 10, enemyCastle.y);
            ctx.closePath();
            ctx.fill();

            // 성 체력 표시
            ctx.fillStyle = "#000000";
            ctx.font = "bold 13px sans-serif";
            ctx.textAlign = "center";
            ctx.fillText(`아군 성 (${playerCastle.hp}/${playerCastle.maxHp})`, playerCastle.x + playerCastle.width / 2, playerCastle.y - 40);
            ctx.fillText(`적군 성 (${enemyCastle.hp}/${enemyCastle.maxHp})`, enemyCastle.x + enemyCastle.width / 2, enemyCastle.y - 40);

            // 성 체력바
            ctx.fillStyle = "#e0e0e0";
            ctx.fillRect(playerCastle.x, playerCastle.y - 35, playerCastle.width, 6);
            ctx.fillRect(enemyCastle.x, enemyCastle.y - 35, enemyCastle.width, 6);
            
            ctx.fillStyle = "#4caf50";
            ctx.fillRect(playerCastle.x, playerCastle.y - 35, playerCastle.width * (playerCastle.hp / playerCastle.maxHp), 6);
            ctx.fillRect(enemyCastle.x, enemyCastle.y - 35, enemyCastle.width * (enemyCastle.hp / enemyCastle.maxHp), 6);

            // 4. 아군 유닛 그리기
            playerUnits.forEach(unit => {
                ctx.fillStyle = unit.color;
                ctx.fillRect(unit.x, unit.y, unit.width, unit.height);
                ctx.strokeStyle = '#000000';
                ctx.lineWidth = 2;
                ctx.strokeRect(unit.x, unit.y, unit.width, unit.height);

                // 고양이 귀
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

                // 유닛 체력바
                ctx.fillStyle = "#ff5252";
                ctx.fillRect(unit.x, unit.y - 8, unit.width, 4);
                ctx.fillStyle = "#4caf50";
                ctx.fillRect(unit.x, unit.y - 8, unit.width * (unit.hp / unit.maxHp), 4);
            });

            // 5. 적군 유닛 그리기
            enemyUnits.forEach(unit => {
                ctx.fillStyle = unit.color;
                ctx.fillRect(unit.x, unit.y, unit.width, unit.height);
                ctx.strokeStyle = '#000000';
                ctx.lineWidth = 2;
                ctx.strokeRect(unit.x, unit.y, unit.width, unit.height);

                // 적 체력바
                ctx.fillStyle = "#ff5252";
                ctx.fillRect(unit.x, unit.y - 8, unit.width, 4);
                ctx.fillStyle = "#4caf50";
                ctx.fillRect(unit.x, unit.y - 8, unit.width * (unit.hp / unit.maxHp), 4);
            });

            // 게임 오버 문구 표시
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

components.html(game_code, height=420)
