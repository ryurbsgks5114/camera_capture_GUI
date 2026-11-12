
import tkinter as tk

from config import WHITE, TEXT

from common.ui.common import create_panel

from system.status.service.system_status_display import build_system_status_display_items


def build(parent, app):
    """시스템 상태 UI를 생성합니다.

    Args:
        parent (tk.Widget): 시스템 상태 패널을 배치할 부모 위젯
        app (CameraManagerApp): 애플리케이션 인스턴스

    Returns:
        tk.Frame: 생성된 시스템 상태 패널
    """

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


def refresh(app):
    """시스템 상태 UI를 갱신합니다.

    Args:
        app (CameraManagerApp): 애플리케이션 인스턴스
    """

    # 기존 상태 위젯 초기화
    for widget in app.system_body.winfo_children():
        widget.destroy()

    # 상태 표시 데이터 가져오기
    display_items = build_system_status_display_items(app.state)

    # 2열 배치
    for index, (label, value, color) in enumerate(display_items):
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
