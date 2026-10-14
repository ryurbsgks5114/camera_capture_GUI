import tkinter as tk
from config import WHITE, BORDER, TEXT, GREEN, GRAY, GRAY_LIGHT, RED, BLUE
from ui.common import create_panel

# ==========================================
# 촬영 제어 UI 및 기능 함수
# ==========================================
def build(parent, app):
    # 상위 패널 생성
    panel = create_panel(parent, "촬영 제어")
    panel.pack(fill="both", expand=True, pady=5)

    # 버튼 및 내부 바디 생성
    body = tk.Frame(panel, bg=WHITE)
    body.pack(fill="both", expand=True, padx=18, pady=14)
    app.control_body = body

    # 촬영 상태별 UI 생성 함수
    def create_capture_state(title, status_color, card_bg, button_text, button_bg, show_details):
        # 프레임 생성
        card = tk.Frame(body, bg=card_bg, highlightbackground=BORDER, highlightthickness=1)

        # 상태 표시 등, 상태 타이틀 라벨 생성
        tk.Label(
            card,
            text="●",
            bg=card_bg,
            fg=status_color,
            font=("Arial", 25)
        ).pack(pady=(16, 0))
        tk.Label(
            card,
            text=title,
            bg=card_bg,
            fg=status_color,
            font=("Malgun Gothic", 14, "bold")
        ).pack(pady=4)

        # 촬영 중인 경우 상세 설정 정보 표시
        if show_details:
            tk.Label(
                card,
                text="촬영 시작 시간",
                bg=card_bg,
                fg=TEXT,
                font=("Malgun Gothic", 8)
            ).pack(pady=(10, 0))
            tk.Label(
                card,
                textvariable=app.state.start_time_display,
                bg=card_bg,
                fg=TEXT,
                font=("Malgun Gothic", 10, "bold")
            ).pack()
            tk.Label(
                card,
                text="촬영 간격",
                bg=card_bg,
                fg=TEXT,
                font=("Malgun Gothic", 8)
            ).pack(pady=(5, 0))
            tk.Label(
                card,
                textvariable=app.state.interval_display,
                bg=card_bg,
                fg=TEXT,
                font=("Malgun Gothic", 10, "bold")
            ).pack()

        # 제어 버튼 생성(촬영 시작 / 촬영 중지)
        button = tk.Button(
            card,
            text=button_text,
            bg=button_bg,
            fg=WHITE,
            activebackground=button_bg,
            activeforeground=WHITE,
            relief="flat",
            bd=0,
            font=("Malgun Gothic", 11, "bold"),
            padx=15,
            pady=10
        )
        button.pack(fill="x", padx=16, pady=(12, 16))

        return card, button

    # 대기 중 상태 UI 생성
    idle_card, idle_button = create_capture_state("대기 중", GRAY, GRAY_LIGHT, "▶  촬영 시작", BLUE, False)
    idle_card.pack(fill="both", expand=True)

    # 촬영 중 상태 UI 생성
    running_card, running_button = create_capture_state("촬영 중", GREEN, "#EDF9F2", "■  촬영 중지", RED, True)
    running_card.pack_forget()

    # 상태 전환 함수(대기 중 -> 촬영 중)
    def show_running():
        idle_card.pack_forget()
        running_card.pack(fill="both", expand=True)
        app.state.capture_status.set("촬영 중")
        app.refresh_system_status()
        app.notify("촬영이 진행 중입니다.")

    # 상태 전환 함수(촬영 중 -> 대기 중)
    def show_idle():
        running_card.pack_forget()
        idle_card.pack(fill="both", expand=True)
        app.state.capture_status.set("대기 중")
        app.refresh_system_status()
        app.notify("촬영이 대기 상태입니다.")

    # 버튼에 클릭 이벤트 핸들러 바인딩
    idle_button.configure(command=show_running)
    running_button.configure(command=show_idle)