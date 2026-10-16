import tkinter as tk
from config import WHITE, BORDER, TEXT, GREEN, GRAY, GRAY_LIGHT, RED, BLUE
from services.capture_start_validator import validate_capture_start_settings
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
            disabledforeground=WHITE,
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

    # ==========================================
    # 내부 촬영 상태
    # idle: 대기 중
    # starting: 촬영 시작 처리 중
    # running: 촬영 중
    # ==========================================
    capture_state = "idle"

    # 상태 전환 함수(대기 중 -> 촬영 중)
    def show_running():
        nonlocal capture_state
        capture_state = "running"

        app.set_capture_settings_locked(True)
        
        idle_card.pack_forget()
        running_card.pack(fill="both", expand=True)
        app.state.capture_status.set("촬영 중")
        app.refresh_system_status()
        app.notify("촬영이 진행 중입니다.", GREEN)

    # 상태 전환 함수(촬영 중 -> 대기 중)
    def show_idle():
        nonlocal capture_state
        capture_state = "idle"

        app.set_capture_settings_locked(False)

        running_card.pack_forget()
        idle_card.pack(fill="both", expand=True)

        # 버튼 상태 복구
        idle_button.configure(
            state=tk.NORMAL,
            text="▶  촬영 시작"
        )

        app.state.capture_status.set("대기 중")
        app.refresh_system_status()
        app.notify("촬영이 대기 상태입니다.")

    # 촬영 시작 버튼 클릭 시 설정값 검증
    def start_capture():
        nonlocal capture_state

        # 촬영 시작 처리 중이거나 이미 촬영 중이면 중복 실행 방지
        if capture_state != "idle":
            return

        # 이후 작업이 진행되는 동안 중복 클릭 차단
        capture_state = "starting"
        idle_button.configure(
            state=tk.DISABLED,
            text="촬영 시작 대기 중..."
        )

        valid, message = validate_capture_start_settings(
            hour_text=app.state.hour_var.get(),
            minute_text=app.state.minute_var.get(),
            second_text=app.state.second_var.get(),
            interval_text=app.state.interval_var.get(),
            storage_mode=app.state.storage_mode.get(),
            local_path=app.state.local_path.get(),
            ftp_host=app.state.ftp_host.get(),
            ftp_port=app.state.ftp_port.get(),
            ftp_user=app.state.ftp_user.get(),
            ftp_password=app.state.ftp_password.get(),
            ftp_path=app.state.ftp_path.get()
        )

        # 검증 실패 시 안내 메시지를 표시하고 촬영을 시작하지 않음
        if not valid:
            capture_state = "idle"
            idle_button.configure(
                state=tk.NORMAL,
                text="▶  촬영 시작"
            )

            app.notify(message, RED)

            return

        # 검증을 통과한 경우에만 촬영 상태로 변경
        show_running()

    # 버튼에 클릭 이벤트 핸들러 바인딩
    idle_button.configure(command=start_capture)
    running_button.configure(command=show_idle)