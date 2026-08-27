import random
import tkinter as tk


class InfiniteStairs:

    def __init__(self, root):
        self.root = root
        self.root.title("무한의 계단")
        self.root.geometry("400x600")
        self.root.resizable(False, False)

        # 게임 변수 초기화
        self.score = 0
        self.player_dir = 0  # 0: 왼쪽, 1: 오른쪽
        self.player_x = 200  # 캐릭터 X 좌표
        self.stairs = []  # 계단 방향 리스트
        self.game_over = False

        # 캔버스 생성
        self.canvas = tk.Canvas(root, width=400, height=600, bg="#1a1a2e")
        self.canvas.pack(fill="both", expand=True)

        # 키보드 이벤트 바인딩
        self.root.bind("<Left>", self.on_left_key)
        self.root.bind("<Right>", self.on_right_key)

        self.start_game()

    def start_game(self):
        self.score = 0
        self.player_dir = 0
        self.player_x = 200
        self.game_over = False

        # 첫 번째 계단은 캐릭터 발밑, 이후 계단 랜덤 생성
        self.stairs = [0]
        for _ in range(20):
            self.stairs.append(random.choice([0, 1]))

        self.draw()

    def draw(self):
        self.canvas.delete("all")

        if self.game_over:
            self.canvas.create_text(
                200,
                250,
                text="GAME OVER",
                fill="#e94560",
                font=("Arial", 30, "bold"),
            )
            self.canvas.create_text(
                200,
                310,
                text=f"최종 점수: {self.score}",
                fill="white",
                font=("Arial", 18),
            )
            self.canvas.create_text(
                200,
                380,
                text="좌/우 방향키를 누르면\n다시 시작합니다",
                fill="#a6a6a6",
                font=("Arial", 14),
                justify="center",
            )
            return

        # 점수 표시
        self.canvas.create_text(
            200,
            50,
            text=f"점수: {self.score}",
            fill="white",
            font=("Arial", 22, "bold"),
        )

        # 계단 그리기 (아래에서 위로)
        base_x = self.player_x
        base_y = 450  # 캐릭터 발밑 위치

        # 현재 발밑 계단
        self.canvas.create_rectangle(
            base_x - 30,
            base_y,
            base_x + 30,
            base_y + 15,
            fill="#0f3460",
            outline="#16213e",
        )

        # 다가올 계단들
        curr_x = base_x
        curr_y = base_y
        for i in range(1, 12):
            direction = self.stairs[i]
            if direction == 0:  # 왼쪽
                curr_x -= 40
            else:  # 오른쪽
                curr_x += 40
            curr_y -= 35

            self.canvas.create_rectangle(
                curr_x - 30,
                curr_y,
                curr_x + 30,
                curr_y + 15,
                fill="#e94560" if i == 1 else "#0f3460",
                outline="#16213e",
            )

        # 캐릭터 그리기 (노란색 원)
        self.canvas.create_oval(
            base_x - 15,
            base_y - 30,
            base_x + 15,
            base_y,
            fill="#fbc531",
            outline="white",
        )

        # 캐릭터 시선 방향 표시
        eye_x = base_x - 7 if self.player_dir == 0 else base_x + 7
        self.canvas.create_oval(
            eye_x - 3, base_y - 20, eye_x + 3, base_y - 14, fill="black"
        )

    def process_move(self, input_dir):
        if self.game_over:
            self.start_game()
            return

        # 입력받은 방향으로 캐릭터 방향 변경
        self.player_dir = input_dir

        # 다음 계단 방향과 캐릭터 입력 방향이 일치하는지 검사
        next_stair_dir = self.stairs[1]

        if self.player_dir == next_stair_dir:
            # 성공: 점수 증가 및 계단 이동
            self.score += 1
            self.stairs.pop(0)
            self.stairs.append(random.choice([0, 1]))
            self.draw()
        else:
            # 실패: 게임 오버
            self.game_over = True
            self.draw()

    def on_left_key(self, event):
        self.process_move(0)

    def on_right_key(self, event):
        self.process_move(1)


if __name__ == "__main__":
    root = tk.Tk()
    app = InfiniteStairs(root)
    root.mainloop()
