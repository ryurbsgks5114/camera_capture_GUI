import tkinter as tk
from tkinter import ttk
from datetime import datetime
from config import WHITE, GRAY, TEXT
from ui.common import create_panel

# ==========================================
# 알림 UI 및 기능 함수
# ==========================================
def build(parent, app):
    # 상위 패널 생성
    panel = create_panel(parent, "알림")
    panel.pack(fill="both", expand=True, pady=5)

    # 알림 로그를 담을 내부 영역 생성
    area = tk.Frame(panel, bg=WHITE)
    area.pack(fill="both", expand=True, padx=18, pady=10)

    # 스크롤 가능한 캔버스 및 수직 스크롤바 생성
    canvas = tk.Canvas(area, bg=WHITE, highlightthickness=0)
    scrollbar = ttk.Scrollbar(area, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    # 스크롤바와 캔버스 배치
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # 실제 로그 항목들이 쌓일 내부 프레임 생성 및 캔버스 윈도우에 등록
    notice_list = tk.Frame(canvas, bg=WHITE)
    window = canvas.create_window((0, 0), window=notice_list, anchor="nw")

    # ==========================================
    # 캔버스 내부 내용 크기 변경 시 스크롤 영역을 갱신하는 함수
    # ==========================================
    def update_scrollregion(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))

    # ==========================================
    # 캔버스 크기 변경 시 내부 프레임의 너비를 캔버스 크기에 맞추는 함수
    # ==========================================
    def resize_list(event):
        canvas.itemconfigure(window, width=event.width)

    # 이벤트 바인딩 설정
    notice_list.bind("<Configure>", update_scrollregion)
    canvas.bind("<Configure>", resize_list)

    # ==========================================
    # 새로운 알림 로그를 화면에 추가하고 가장 아래로 스크롤을 이동하는 함수
    # ==========================================
    def add_notice(message, color=TEXT):
        # 현재 시각 포맷팅(시:분:초)
        now = datetime.now().strftime("%H:%M:%S")

        # 개별 로그 행 생성
        row = tk.Frame(notice_list, bg=WHITE)
        row.pack(fill="x", pady=5)

        # 로그 발생 시각 생성
        tk.Label(
            row,
            text=now,
            bg=WHITE,
            fg=GRAY,
            font=("Malgun Gothic", 8),
            width=8,
            anchor="w"
        ).pack(side="left")

        # 알림 메시지 생성
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

        # UI 렌더링 강제 업데이트 후 스크롤을 최하단으로 이동
        canvas.update_idletasks()
        canvas.yview_moveto(1.0)

    # 애플리케이션 전역에서 알림을 출력할 수 있도록 app.notify에 함수 등록
    app.notify = add_notice
    # 프로그램 실행 초기 안내 알림 메시지 추가
    add_notice("프로그램이 실행되었습니다.")