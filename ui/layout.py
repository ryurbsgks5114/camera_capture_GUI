
import tkinter as tk
from tkinter import ttk
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

    # 현재 날짜와 시간 갱신
    def update_datetime():
        now = datetime.now()
        weekdays = ["월", "화", "수", "목", "금", "토", "일"]

        datetime_text = "{} ({}) {}".format(
            now.strftime("%Y-%m-%d"),
            weekdays[now.weekday()],
            now.strftime("%H:%M")
        )

        datetime_label.config(text=datetime_text)

        delay = (60 - now.second) * 1000 - now.microsecond // 1000
        root.after(max(delay, 1), update_datetime)

    update_datetime()


# ==========================================
# 메인 화면 레이아웃 및 스크롤 영역 생성 함수
# ==========================================
def build_main(root):
    # 메인 화면 스크롤 영역 컨테이너
    viewport = tk.Frame(root, bg=BG)
    viewport.pack(fill="both", expand=True, padx=14, pady=14)

    # 스크롤 가능한 캔버스
    canvas = tk.Canvas(
        viewport,
        bg=BG,
        highlightthickness=0,
        borderwidth=0
    )

    # 가로 스크롤바
    horizontal_scrollbar = ttk.Scrollbar(
        viewport,
        orient="horizontal",
        command=canvas.xview
    )

    # 세로 스크롤바
    vertical_scrollbar = ttk.Scrollbar(
        viewport,
        orient="vertical",
        command=canvas.yview
    )

    # 캔버스와 스크롤바 연결
    canvas.configure(
        xscrollcommand=horizontal_scrollbar.set,
        yscrollcommand=vertical_scrollbar.set
    )

    # 컨테이너 배치 설정
    viewport.grid_rowconfigure(0, weight=1)
    viewport.grid_columnconfigure(0, weight=1)

    canvas.grid(row=0, column=0, sticky="nsew")
    vertical_scrollbar.grid(row=0, column=1, sticky="ns")
    horizontal_scrollbar.grid(row=1, column=0, sticky="ew")

    # 실제 UI가 배치될 내부 프레임
    main = tk.Frame(canvas, bg=BG)

    main_window = canvas.create_window(
        (0, 0),
        window=main,
        anchor="nw"
    )

    # ==========================================
    # 내부 화면 크기 및 스크롤 영역 갱신
    # ==========================================
    def update_content_size(event=None):
        if not canvas.winfo_exists() or not main.winfo_exists():
            return

        # 내부 UI가 요구하는 최소 크기
        required_width = main.winfo_reqwidth()
        required_height = main.winfo_reqheight()

        # 창이 작아져도 내부 UI의 최소 크기는 유지
        content_width = max(
            canvas.winfo_width(),
            required_width
        )

        content_height = max(
            canvas.winfo_height(),
            required_height
        )

        # 내부 프레임 크기 적용
        canvas.itemconfigure(
            main_window,
            width=content_width,
            height=content_height
        )

        # 스크롤 가능한 전체 영역 설정
        canvas.configure(
            scrollregion=(0, 0, content_width, content_height)
        )

    # 내부 위젯 크기 변경 시 갱신
    main.bind("<Configure>", update_content_size)

    # GUI 창 크기 변경 시 갱신
    canvas.bind("<Configure>", update_content_size)

    # ==========================================
    # 기존 3열 레이아웃 유지
    # ==========================================
    main.grid_columnconfigure(0, weight=30)
    main.grid_columnconfigure(1, weight=36)
    main.grid_columnconfigure(2, weight=34)
    main.grid_rowconfigure(0, weight=1)

    # 좌측 영역
    left = tk.Frame(main, bg=BG)
    left.grid(
        row=0,
        column=0,
        sticky="nsew",
        padx=(0, 7)
    )

    # 중앙 영역
    center = tk.Frame(main, bg=BG)
    center.grid(
        row=0,
        column=1,
        sticky="nsew",
        padx=7
    )

    # 우측 영역
    right = tk.Frame(main, bg=BG)
    right.grid(
        row=0,
        column=2,
        sticky="nsew",
        padx=(7, 0)
    )

    return main, left, center, right