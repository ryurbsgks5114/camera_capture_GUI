
import tkinter as tk

from config import WHITE, TEXT, GREEN, GRAY, RED
from ui.common import create_panel


# ==========================================
# 상태에 따라 색상 코드 반환
# ==========================================
def get_status_color(status):
    if status in ("연결 성공", "연결됨", "촬영 중"):
        return GREEN

    if status == "연결 실패":
        return RED

    return GRAY


# ==========================================
# 시스템 상태 UI 생성
# ==========================================
def build(parent, app):
    panel = create_panel(parent, "시스템 상태")

    # 시스템 상태 패널의 세로 여백 축소
    panel.pack(fill="x", pady=(0, 5))

    # 공통 패널 헤더 여백 축소
    header = panel.winfo_children()[0]
    header.pack_configure(
        padx=12,
        pady=(7, 4)
    )

    # 상태 항목 표시 영역
    app.system_body = tk.Frame(
        panel,
        bg=WHITE
    )
    app.system_body.pack(
        fill="x",
        padx=12,
        pady=(4, 6)
    )

    # 최초 상태 표시
    refresh(app)

    return panel


# ==========================================
# 시스템 상태 갱신
# ==========================================
def refresh(app):
    # 기존 상태 위젯 초기화
    for widget in app.system_body.winfo_children():
        widget.destroy()

    statuses = [
        ("서버 상태", app.state.server_status.get()),
        ("WS 상태", app.state.websocket_status.get()),
        ("촬영 상태", app.state.capture_status.get()),
        ("FTP 상태", app.state.ftp_status.get())
    ]

    # 2열 배치
    for index, (label, value) in enumerate(statuses):
        row = index // 2
        column = index % 2

        item = tk.Frame(
            app.system_body,
            bg=WHITE
        )
        item.grid(
            row=row,
            column=column,
            sticky="w",
            padx=(0, 8),
            pady=3
        )

        # 상태 항목 이름
        tk.Label(
            item,
            text=label,
            width=8,
            anchor="w",
            bg=WHITE,
            fg=TEXT,
            font=("Malgun Gothic", 9)
        ).pack(side="left")

        # 상태에 따른 색상
        color = get_status_color(value)

        # 상태 표시 원
        canvas = tk.Canvas(
            item,
            width=12,
            height=12,
            bg=WHITE,
            highlightthickness=0
        )
        canvas.pack(
            side="left",
            padx=(0, 5)
        )

        canvas.create_oval(
            2,
            2,
            10,
            10,
            fill=color,
            outline=color
        )

        # 상태 텍스트
        tk.Label(
            item,
            text=value,
            bg=WHITE,
            fg=color,
            font=("Malgun Gothic", 9, "bold")
        ).pack(side="left")

    # 두 열의 너비를 동일하게 유지
    app.system_body.grid_columnconfigure(0, weight=1)
    app.system_body.grid_columnconfigure(1, weight=1)
