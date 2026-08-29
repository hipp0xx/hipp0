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
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="600" height="300"></canvas>
    <div id="info"><b>조작법:</b> 화면 클릭 또는 스페이스바 누르고 있기 (상승) / 떼기 (하강)</div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        // 게임 변수
        let isPressing = false;
        let gameOver = false;
        let score = 0;

        // 플레이어 (Wave)
        const player = {
            x: 80,
            y: canvas.height / 2,
            size: 12,
            speedY: 4
        };

        // 장애물
        let obstacles = [];
        let frameCount = 0;

        // 입력을 감지하는 이벤트 리스너
