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
        <button id="btnBasic" onclick="spawnUnit('basic')">🐱 기본 (50원)</button>
        <button id="btnTank" onclick="spawnUnit('tank')">🦒 탱커 (75원)</button>
    </div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        const groundY = 220;

        // 재화(돈) 및 쿨타임 시스템 데이터
        let money = 0;
        const maxMoney = 1000;
        const moneyIncomeRate = 0.5; // 프레임당 증가하는 돈

        const unitConfigs = {
            basic: { cost: 50, cooldown: 500, hp: 30, atk: 10, speed: 1.2, width: 25, height: 25, color: '#ffffff' },
            tank:  { cost: 75, cooldown: 1000, hp: 60, atk: 7,  speed: 0.6, width: 20, height: 50, color: '#ffffff' }
        };

        const cooldownState = {
            basic: { ready: true, timer: null },
            tank:  { ready: true, timer: null }
        };

        // 성 설정
        const playerCastle = { x: 50, y: groundY - 80, width: 60, height: 80, hp: 1000 };
        const enemyCastle = { x: 690, y: groundY - 80, width: 60, height: 80, hp: 1000 };

        // 유닛 목록
        const units = [];

        // 유닛 소환 처리
        function spawnUnit(type) {
            const config = unitConfigs[type];

            // 돈 부전 또는 쿨타임 중이면 소환 불가
            if (money < config.cost || !cooldownState[type].ready) return;

            // 돈 차감
            money -= config.cost;

            // 쿨타임 적용
            cooldownState[type].ready = false;
            setTimeout(() => {
                cooldownState[type].ready = true;
            }, config.cooldown);

            // 유닛 생성
            units.push({
                x: playerCastle.x + playerCastle.width,
                y: groundY - config.height,
                width: config.width,
                height: config.height,
                speed: config.speed,
                hp: config.hp,
                maxHp: config.hp,
                atk: config.atk,
                color: config.color,
                type: type
            });
        }

        function updateUI() {
            // 돈 텍스트 업데이트
            document.getElementById("moneyTxt").innerText = Math.floor(money);

            // 버튼 상태 업데이트 (비용 + 쿨타임 체크)
            const btnBasic = document.getElementById("btnBasic");
            const btnTank = document.getElementById("btnTank");

            btnBasic.disabled = (money < unitConfigs.basic.cost) || !cooldownState.basic.ready;
            btnTank.disabled = (money < unitConfigs.tank.cost) || !cooldownState.tank.ready;
        }

        function update() {
            // 돈 수급
            if (money < maxMoney) {
                money = Math.min(maxMoney, money + moneyIncomeRate);
            }

            // 유닛 이동
            units.forEach(unit => {
                if (unit.x + unit.width < enemyCastle.x) {
                    unit.x += unit.speed;
                }
            });

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

            // 성 이름
            ctx.fillStyle = "#000000";
            ctx.font = "bold 14px sans-serif";
            ctx.textAlign = "center";
            ctx.fillText("아군 성", playerCastle.x + playerCastle.width / 2, playerCastle.y - 40);
            ctx.fillText("적군 성", enemyCastle.x + enemyCastle.width / 2, enemyCastle.y - 40);

            // 4. 유닛 그리기
            units.forEach(unit => {
                ctx.fillStyle = unit.color;
                ctx.fillRect(unit.x, unit.y, unit.width, unit.height);
                ctx.strokeStyle = '#000000';
                ctx.lineWidth = 2;
                ctx.strokeRect(unit.x, unit.y, unit.width, unit.height);

                // 고양이 귀 표현
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
            });
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
