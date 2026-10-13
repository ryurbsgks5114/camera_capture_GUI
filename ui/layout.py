import tkinter as tk
from datetime import datetime
from config import BG, WHITE, TEXT, SUBTEXT

# ==========================================
# 상단 헤더 UI 생성 함수
# ==========================================
def build_header(root):
    # 상단 헤더 프레임 생성 및 고정 높이 설정
    header = tk.Frame(root, bg=WHITE, height=70)
    header.pack(fill="x")
    header.pack_propagate(False)

    # 프로그램 제목
    tk.Label(
        header,
        text="📷  Camera Manager",
        bg=WHITE,
        fg=TEXT,
        font=("Malgun Gothic", 18, "bold")
    ).pack(side="left", padx=24)

    # 날짜 및 시간 표시
    datetime_label = tk.Label(
        header,
        text="",
        bg=WHITE,
        fg=SUBTEXT,
        font=("Malgun Gothic", 9)
    )
    datetime_label.pack(side="right", padx=24)

    # 현재 날짜와 시간을 계산하여 1분 주기로 재호출하는 함수
    def update_datetime():
        now = datetime.now()
        weekdays = ["월", "화", "수", "목", "금", "토", "일"]

        datetime_text = "{} ({}) {}".format(
            now.strftime("%Y-%m-%d"),
            weekdays[now.weekday()],
            now.strftime("%H:%M")
        )

        datetime_label.config(text=datetime_text)

        # 다음 분이 시작되는 정각에 맞춰 갱신되도록 딜레이 계산 후 root.after 예약
        delay = (60 - now.second) * 1000 - now.microsecond // 1000
        root.after(max(delay, 1), update_datetime)

    # 시계 기능 최초 실행
    update_datetime()

# ==========================================
# 메인 화면 레이아웃(3분할 그리드)을 생성하는 함수
# ==========================================
def build_main(root):
    # 메인 컨테이너 프레임 생성 및 배치
    main = tk.Frame(root, bg=BG)
    main.pack(fill="both", expand=True, padx=14, pady=14)

    # 3개 컬럼의 가로 비율 설정
    main.grid_columnconfigure(0, weight=30)
    main.grid_columnconfigure(1, weight=36)
    main.grid_columnconfigure(2, weight=34)
    main.grid_rowconfigure(0, weight=1)

    # 좌측 영역 프레임 생성 및 배치
    left = tk.Frame(main, bg=BG)
    left.grid(row=0, column=0, sticky="nsew", padx=(0, 7))

    # 중앙 영역 프레임 생성 및 배치
    center = tk.Frame(main, bg=BG)
    center.grid(row=0, column=1, sticky="nsew", padx=7)

    # 우측 영역 프레임 생성 및 배치
    right = tk.Frame(main, bg=BG)
    right.grid(row=0, column=2, sticky="nsew", padx=(7, 0))

    return main, left, center, right
