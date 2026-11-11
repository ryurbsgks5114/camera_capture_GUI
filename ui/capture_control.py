
import tkinter as tk
import threading

from config import (
    WHITE,
    BORDER,
    TEXT,
    GREEN,
    GRAY,
    GRAY_LIGHT,
    RED,
    BLUE,
    FTP_HOST,
    FTP_PORT,
    FTP_USER,
    FTP_PASSWORD
)
from services.capture_start_validator import validate_capture_start_settings
from services.api_client import (
    start_capture as request_start_capture,
    stop_capture as request_stop_capture,
)
from ui.common import create_panel


# ==========================================
# 촬영 제어 UI 및 기능 함수
# ==========================================
def build(parent, app):
    # 상위 패널 생성
    panel = create_panel(parent, "촬영 제어")
    panel.configure(height=120)
    panel.pack(fill="both", expand=False, pady=5)
    panel.pack_propagate(False)

    # 버튼 및 내부 바디 생성
    body = tk.Frame(panel, bg=WHITE)
    body.pack(fill="both", expand=True, padx=18, pady=9)
    app.control_body = body

    # ==========================================
    # 촬영 상태별 UI 생성 함수
    # ==========================================
    def create_capture_state(title, status_color, card_bg, button_text, button_bg, show_details):
        card = tk.Frame(
            body,
            bg=card_bg,
            highlightbackground=BORDER,
            highlightthickness=1,
            height=56
        )
        card.pack_propagate(False)

        status_frame = tk.Frame(card, bg=card_bg)
        status_frame.pack(side="left", fill="y", padx=(12, 0))

        tk.Label(
            status_frame,
            text="●",
            bg=card_bg,
            fg=status_color,
            font=("Arial", 12)
        ).pack(side="left", padx=(0, 7), pady=(0, 4))

        tk.Label(
            status_frame,
            text=title,
            bg=card_bg,
            fg=status_color,
            font=("Malgun Gothic", 10, "bold"),
            anchor="center"
        ).pack(side="left")

        if show_details:
            tk.Label(
                status_frame,
                textvariable=app.state.start_time_display,
                bg=card_bg,
                fg=TEXT,
                font=("Malgun Gothic", 8)
            ).pack(side="left", padx=(12, 0))

            tk.Label(
                status_frame,
                textvariable=app.state.interval_display,
                bg=card_bg,
                fg=TEXT,
                font=("Malgun Gothic", 8)
            ).pack(side="left", padx=(8, 0))

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
            font=("Malgun Gothic", 9, "bold"),
            padx=10,
            pady=5
        )
        button.pack(side="right", padx=8, pady=5)

        return card, button

    # 대기 중 상태 UI 생성
    idle_card, idle_button = create_capture_state(
        "대기 중",
        GRAY,
        GRAY_LIGHT,
        "▶ 촬영 시작",
        BLUE,
        False
    )
    idle_card.pack(fill="x", expand=True)

    # 촬영 중 상태 UI 생성
    running_card, running_button = create_capture_state(
        "촬영 중",
        GREEN,
        "#EDF9F2",
        "■ 촬영 중지",
        RED,
        False
    )
    running_card.pack_forget()

    # ==========================================
    # 내부 촬영 상태
    # ==========================================
    capture_state = "idle"

    # ==========================================
    # 상태 전환 함수(대기 중 -> 촬영 중)
    # ==========================================
    def show_running():
        nonlocal capture_state
        capture_state = "running"

        app.set_capture_settings_locked(True)

        idle_card.pack_forget()
        running_card.pack(fill="x", expand=True)

        running_button.configure(
            state=tk.NORMAL,
            text="■ 촬영 중지"
        )

        # FTP 저장 모드에서 서버의 촬영 시작 응답이 성공했다면
        # 서버 측 FTP 연결 및 저장 경로 확인도 통과한 상태
        if app.state.storage_mode.get() in ("ftp", "both"):
            app.state.ftp_status.set("연결 성공")

        app.state.server_status.set("연결 성공")
        app.state.capture_status.set("촬영 중")
        app.refresh_system_status()

    # ==========================================
    # 상태 전환 함수(촬영 중 -> 대기 중)
    # ==========================================
    def show_idle():
        nonlocal capture_state
        capture_state = "idle"

        app.set_capture_settings_locked(False)

        running_card.pack_forget()
        idle_card.pack(fill="x", expand=True)

        idle_button.configure(
            state=tk.NORMAL,
            text="▶ 촬영 시작"
        )

        app.state.capture_status.set("대기 중")
        app.refresh_system_status()

    # ==========================================
    # 촬영 설정값 검증 및 촬영 시작 요청 함수
    # ==========================================
    def start_capture():
        nonlocal capture_state

        if capture_state != "idle":
            return

        capture_state = "starting"
        idle_button.configure(
            state=tk.DISABLED,
            text="촬영 시작 대기 중..."
        )

        # FTP 접속정보 검증은 하지 않고 저장 경로 선택 여부만 확인
        valid, message = validate_capture_start_settings(
            hour_text=app.state.hour_var.get(),
            minute_text=app.state.minute_var.get(),
            second_text=app.state.second_var.get(),
            interval_text=app.state.interval_var.get(),
            storage_mode=app.state.storage_mode.get(),
            local_path=app.state.local_path.get(),
            ftp_path=app.state.ftp_path.get()
        )

        if not valid:
            capture_state = "idle"
            idle_button.configure(
                state=tk.NORMAL,
                text="▶ 촬영 시작"
            )

            app.notify(message, RED)
            return

        # 서버에 전달할 촬영 설정 구성
        payload = {
            "start_time": "{}:{}:{}".format(
                app.state.hour_var.get().strip(),
                app.state.minute_var.get().strip(),
                app.state.second_var.get().strip()
            ),
            "interval_minutes": int(app.state.interval_var.get().strip()),
            "storage_mode": app.state.storage_mode.get()
        }

        # local / both 모드에서는 로컬 저장 경로 전달
        if payload["storage_mode"] in ("local", "both"):
            payload["local_path"] = app.state.local_path.get().strip()

        # FTP / both 모드에서는 config.py의 FTP 접속정보 사용
        if payload["storage_mode"] in ("ftp", "both"):
            payload["ftp"] = {
                "host": FTP_HOST,
                "port": int(FTP_PORT),
                "user": FTP_USER,
                "password": FTP_PASSWORD,
                "base_dir": app.state.ftp_path.get().strip()
            }

        app.notify("서버에 촬영 시작 요청을 보내는 중입니다...", BLUE)

        # 네트워크 요청 중 GUI가 멈추지 않도록 별도 스레드에서 요청
        def send_start_request():
            try:
                response = request_start_capture(payload)
            except Exception as error:
                app.root.after(
                    0,
                    lambda error=str(error): handle_start_failure(error)
                )
                return

            app.root.after(
                0,
                lambda response=response: handle_start_success(response)
            )

        threading.Thread(target=send_start_request, daemon=True).start()

    # ==========================================
    # API 요청 성공 콜백 함수
    # ==========================================
    def handle_start_success(response):
        show_running()
        app.notify(response.get("message", "촬영을 시작했습니다."), GREEN)

    # ==========================================
    # API 요청 실패 콜백 함수
    # ==========================================
    def handle_start_failure(message):
        nonlocal capture_state
        capture_state = "idle"

        idle_button.configure(
            state=tk.NORMAL,
            text="▶ 촬영 시작"
        )

        server_unreachable = message.startswith("서버에 연결할 수 없습니다.")

        if server_unreachable:
            app.state.server_status.set("연결 실패")
        else:
            # 서버가 응답했다면 서버 연결은 성공한 상태
            app.state.server_status.set("연결 성공")

            # FTP 저장 모드에서 FTP 오류가 발생한 경우
            # FTP 상태만 실패로 변경
            if (
                app.state.storage_mode.get() in ("ftp", "both")
                and "FTP" in message.upper()
            ):
                app.state.ftp_status.set("연결 실패")

        app.refresh_system_status()
        app.notify(message, RED)

    # ==========================================
    # 촬영 중지 요청 함수
    # ==========================================
    def stop_capture():
        nonlocal capture_state

        if capture_state != "running":
            return

        capture_state = "stopping"
        running_button.configure(
            state=tk.DISABLED,
            text="중지 요청 중..."
        )

        app.notify("서버에 촬영 중지 요청을 보내는 중입니다...", BLUE)

        def send_stop_request():
            try:
                response = request_stop_capture()
            except Exception as error:
                app.root.after(
                    0,
                    lambda error=str(error): handle_stop_failure(error)
                )
                return

            app.root.after(
                0,
                lambda response=response: handle_stop_success(response)
            )

        threading.Thread(target=send_stop_request, daemon=True).start()

    # ==========================================
    # API 요청 성공 콜백 함수
    # ==========================================
    def handle_stop_success(response):
        show_idle()
        app.notify(response.get("message", "촬영을 중지했습니다."), GREEN)

    # ==========================================
    # API 요청 실패 콜백 함수
    # ==========================================
    def handle_stop_failure(message):
        nonlocal capture_state
        capture_state = "running"

        running_button.configure(
            state=tk.NORMAL,
            text="■ 촬영 중지"
        )

        app.notify(message, RED)

    # 버튼 이벤트 연결
    idle_button.configure(command=start_capture)
    running_button.configure(command=stop_capture)
