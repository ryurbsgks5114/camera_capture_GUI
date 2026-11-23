
import tkinter as tk

from datetime import datetime
from tkinter import ttk

from config import BG, WHITE, TEXT, SUBTEXT


def build_header(root):
    """프로그램 상단 헤더 UI를 생성합니다.

    프로그램 제목과 현재 날짜 및 시간을 표시하며,
    분 단위로 날짜와 시간 표시를 갱신합니다.

    Args:
        root (tk.Tk): 애플리케이션 최상위 윈도우
    """
    header = tk.Frame(root, bg=WHITE, height=60)
    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(
        header,
        text="📷  Camera Manager",
        bg=WHITE,
        fg=TEXT,
        font=("Malgun Gothic", 18, "bold")
    ).pack(side="left", padx=24)

    datetime_label = tk.Label(
        header,
        text="",
        bg=WHITE,
        fg=SUBTEXT,
        font=("Malgun Gothic", 9)
    )
    datetime_label.pack(side="right", padx=24)

    def update_datetime():
        """현재 날짜와 시간을 표시하고 다음 갱신을 예약합니다."""
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


def build_main(root):
    """메인 화면의 스크롤 영역과 3열 레이아웃을 생성합니다.

    Args:
        root (tk.Tk): 애플리케이션 최상위 윈도우

    Returns:
        tuple: 메인 프레임과 좌측, 중앙, 우측 영역
    """
    viewport = tk.Frame(root, bg=BG)
    viewport.pack(fill="both", expand=True, padx=14, pady=14)

    canvas = tk.Canvas(
        viewport,
        bg=BG,
        highlightthickness=0,
        borderwidth=0
    )

    horizontal_scrollbar = ttk.Scrollbar(
        viewport,
        orient="horizontal",
        command=canvas.xview
    )

    vertical_scrollbar = ttk.Scrollbar(
        viewport,
        orient="vertical",
        command=canvas.yview
    )

    canvas.configure(
        xscrollcommand=horizontal_scrollbar.set,
        yscrollcommand=vertical_scrollbar.set
    )

    viewport.grid_rowconfigure(0, weight=1)
    viewport.grid_columnconfigure(0, weight=1)

    canvas.grid(row=0, column=0, sticky="nsew")

    main = tk.Frame(canvas, bg=BG)

    main_window = canvas.create_window(
        (0, 0),
        window=main,
        anchor="nw"
    )

    def update_content_size(event=None):
        """콘텐츠 크기에 따라 스크롤 영역과 스크롤바 표시를 갱신합니다.

        Args:
            event (tk.Event, optional): 위젯 크기 변경 이벤트
        """
        if not canvas.winfo_exists() or not main.winfo_exists():
            return

        viewport_width = viewport.winfo_width()
        viewport_height = viewport.winfo_height()

        if viewport_width <= 1 or viewport_height <= 1:
            return

        required_width = main.winfo_reqwidth()
        required_height = main.winfo_reqheight()

        horizontal_width = horizontal_scrollbar.winfo_reqwidth()
        vertical_width = vertical_scrollbar.winfo_reqwidth()
        horizontal_height = horizontal_scrollbar.winfo_reqheight()
        vertical_height = vertical_scrollbar.winfo_reqheight()

        show_horizontal = False
        show_vertical = False

        for _ in range(3):
            available_width = viewport_width
            available_height = viewport_height

            if show_vertical:
                available_width -= vertical_width

            if show_horizontal:
                available_height -= horizontal_height

            next_horizontal = required_width > available_width
            next_vertical = required_height > available_height

            if (next_horizontal == show_horizontal and next_vertical == show_vertical):
                break

            show_horizontal = next_horizontal
            show_vertical = next_vertical

        if show_vertical:
            vertical_scrollbar.grid(row=0, column=1, sticky="ns")
        else:
            vertical_scrollbar.grid_remove()

        if show_horizontal:
            horizontal_scrollbar.grid(row=1, column=0, sticky="ew")
        else:
            horizontal_scrollbar.grid_remove()

        available_width = viewport_width
        available_height = viewport_height

        if show_vertical:
            available_width -= vertical_width

        if show_horizontal:
            available_height -= horizontal_height

        content_width = max(required_width, available_width)
        content_height = max(required_height, available_height)

        canvas.itemconfigure(
            main_window,
            width=content_width,
            height=content_height
        )

        canvas.configure(scrollregion=(0, 0, content_width, content_height))

    main.bind("<Configure>", update_content_size)
    canvas.bind("<Configure>", update_content_size)
    viewport.bind("<Configure>", update_content_size)

    main.grid_columnconfigure(0, minsize=260, weight=1)
    main.grid_columnconfigure(1, minsize=360, weight=1)
    main.grid_columnconfigure(2, minsize=340, weight=1)
    main.grid_rowconfigure(0, weight=1)

    left = tk.Frame(main, bg=BG)
    left.grid(
        row=0,
        column=0,
        sticky="nsew",
        padx=(0, 7)
    )

    center = tk.Frame(main, bg=BG)
    center.grid(
        row=0,
        column=1,
        sticky="nsew",
        padx=7
    )

    right = tk.Frame(main, bg=BG)
    right.grid(
        row=0,
        column=2,
        sticky="nsew",
        padx=(7, 0)
    )

    return main, left, center, right
