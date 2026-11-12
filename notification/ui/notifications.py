
import tkinter as tk

from datetime import datetime
from tkinter import ttk

from config import GRAY, TEXT, WHITE

from common.ui.common import create_panel


def build(parent, app):
    """알림 UI를 생성하고 애플리케이션에 알림 출력 기능을 등록합니다.

    Args:
        parent (tk.Widget): 알림 패널을 배치할 부모 위젯
        app (CameraManagerApp): 애플리케이션 인스턴스
    """
    panel = create_panel(parent, "알림")
    panel.configure(height=392)
    panel.pack(fill="both", expand=False, pady=(0, 5))
    panel.pack_propagate(False)

    # 알림 목록 표시 영역
    area = tk.Frame(panel, bg=WHITE)
    area.pack(fill="both", expand=True, padx=18, pady=10)

    # 스크롤 가능한 알림 영역
    canvas = tk.Canvas(area, bg=WHITE, highlightthickness=0)
    scrollbar = ttk.Scrollbar(area, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # 알림 항목을 배치할 내부 프레임
    notice_list = tk.Frame(canvas, bg=WHITE)
    window = canvas.create_window((0, 0), window=notice_list, anchor="nw")

    def update_scrollregion(event=None):
        """알림 목록의 크기에 맞춰 스크롤 영역을 갱신합니다.

        Args:
            event (tk.Event | None): 위젯 크기 변경 이벤트
        """
        canvas.configure(scrollregion=canvas.bbox("all"))

    def resize_list(event):
        """캔버스 너비에 맞춰 알림 목록의 너비를 조정합니다.

        Args:
            event (tk.Event): 캔버스 크기 변경 이벤트
        """
        canvas.itemconfigure(window, width=event.width)

    def on_mousewheel(event):
        """마우스 휠 입력에 따라 알림 목록을 스크롤합니다.

        Args:
            event (tk.Event): 마우스 휠 이벤트

        Returns:
            str | None: 이벤트 처리를 중단할 경우 "break"
        """
        # 마우스 포인터가 알림 영역 안에 있는지 확인
        left = canvas.winfo_rootx()
        top = canvas.winfo_rooty()
        right = left + canvas.winfo_width()
        bottom = top + canvas.winfo_height()

        if not (left <= event.x_root < right and top <= event.y_root < bottom):
            return

        canvas.update_idletasks()

        bbox = canvas.bbox(window)

        if bbox is None:
            return "break"

        content_height = bbox[3] - bbox[1]
        visible_height = canvas.winfo_height()

        if content_height <= visible_height:
            return "break"

        delta = int(-event.delta / 120)

        if delta == 0:
            return "break"

        canvas.yview_scroll(delta, "units")

        return "break"

    # UI 이벤트 연결
    notice_list.bind("<Configure>", update_scrollregion)
    canvas.bind("<Configure>", resize_list)
    canvas.bind_all("<MouseWheel>", on_mousewheel)

    def add_notice(message, color=TEXT):
        """알림 메시지를 화면에 추가하고 목록을 최하단으로 이동합니다.

        Args:
            message (str): 화면에 표시할 알림 메시지
            color (str): 알림 메시지의 글자 색상
        """
        now = datetime.now().strftime("%H:%M:%S")

        # 알림 항목 생성
        row = tk.Frame(notice_list, bg=WHITE)
        row.pack(fill="x", pady=5)

        # 알림 발생 시각 표시
        tk.Label(
            row,
            text=now,
            bg=WHITE,
            fg=GRAY,
            font=("Malgun Gothic", 8),
            width=8,
            anchor="w"
        ).pack(side="left")

        # 알림 메시지 표시
        tk.Label(
            row,
            text=message,
            bg=WHITE,
            fg=color,
            font=("Malgun Gothic", 9),
            anchor="w",
            justify="left",
            wraplength=300
        ).pack(side="left", fill="x", expand=True)

        # 새 알림이 보이도록 최하단으로 이동
        canvas.update_idletasks()
        canvas.yview_moveto(1.0)

    # 애플리케이션 알림 출력 함수 등록
    app.notify = add_notice

    add_notice("프로그램이 실행되었습니다.")
