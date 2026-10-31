import tkinter as tk
import threading
from config import WHITE, BORDER, TEXT, GREEN, GRAY, GRAY_LIGHT, RED, BLUE
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
    panel.configure(height=460)
    panel.pack(fill="both", expand=False, pady=5)
    panel.pack_propagate(False)

    # 버튼 및 내부 바디 생성
    body = tk.Frame(panel, bg=WHITE)
    body.pack(fill="both", expand=True, padx=18, pady=14)
    app.control_body = body

    # ==========================================
    # 촬영 상태별 UI 생성 함수
    # ==========================================
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
    # - idle: 대기 중
    # - starting: 촬영 시작 처리 중
    # - running: 촬영 중
    # - stopping: 촬영 중지 처리 중
    # ==========================================
    capture_state = "idle"

    # ==========================================
    # 상태 전환 함수(대기 중 -> 촬영 중)
    # ==========================================
    def show_running():
        nonlocal capture_state
        capture_state = "running"

        # 촬영 설정 입력 필드 잠금 처리
        app.set_capture_settings_locked(True)

        # 대기 중 버튼 숨기고 촬영 중 버튼 표시
        idle_card.pack_forget()
        running_card.pack(fill="both", expand=True)

        # 촬영 중지 버튼 상태 초기화
        running_button.configure(
            state=tk.NORMAL,
            text="■  촬영 중지"
        )

        # 시스템 상태 업데이트
        if app.state.storage_mode.get() in ("ftp", "both"):
            app.state.ftp_status.set("연결됨")

        app.state.server_status.set("연결됨")
        app.state.capture_status.set("촬영 중")
        app.refresh_system_status()

    # ==========================================
    # 상태 전환 함수(촬영 중 -> 대기 중)
    # ==========================================
    def show_idle():
        nonlocal capture_state
        capture_state = "idle"

        # 촬영 설정 입력 필드 잠금 해제
        app.set_capture_settings_locked(False)

        # 촬영 중 버튼 숨기고 대기 중 버튼 표시
        running_card.pack_forget()
        idle_card.pack(fill="both", expand=True)

        # 버튼 상태 복구
        idle_button.configure(
            state=tk.NORMAL,
            text="▶  촬영 시작"
        )

        app.state.capture_status.set("대기 중")
        app.refresh_system_status()

    # ==========================================
    # 촬영 설정값 검증 및 촬영 시작 요청 함수
    # ==========================================
    def start_capture():
        nonlocal capture_state

        # 대기 중이 아닌 경우 중복 실행 방지
        if capture_state != "idle":
            return

        # 이후 작업이 진행되는 동안 중복 클릭 차단
        capture_state = "starting"
        idle_button.configure(
            state=tk.DISABLED,
            text="촬영 시작 대기 중..."
        )

        # GUI 입력값 및 설정값 유효성 검증 수행
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

        # GUI에서 검증을 통과하면 라즈베리파이 서버에 실제 촬영 시작 요청
        payload = {
            "start_time": "{}:{}:{}".format(
                app.state.hour_var.get().strip(),
                app.state.minute_var.get().strip(),
                app.state.second_var.get().strip()
            ),
            "interval_minutes": int(app.state.interval_var.get().strip()),
            "storage_mode": app.state.storage_mode.get()
        }

        # local / both 모드에서는 GUI에서 선택한 로컬 저장 경로 전달
        if payload["storage_mode"] in ("local", "both"):
            payload["local_path"] = app.state.local_path.get().strip()

        # FTP 모드에서는 GUI의 FTP 설정을 서버 API에 함께 전달
        if payload["storage_mode"] in ("ftp", "both"):
            payload["ftp"] = {
                "host": app.state.ftp_host.get().strip(),
                "port": int(app.state.ftp_port.get().strip()),
                "user": app.state.ftp_user.get().strip(),
                "password": app.state.ftp_password.get(),
                "base_dir": app.state.ftp_path.get().strip()
            }

        app.notify("라즈베리파이에 촬영 시작 요청을 보내는 중입니다...", BLUE)

        # ==========================================
        # 네트워크 요청 중 GUI가 멈추지 않도록 별도 스레드에서 요청
        # ==========================================
        def send_start_request():
            try:
                response = request_start_capture(payload)
            except Exception as error:
                # 에러 발생 시 메인 스레드에서 실패 핸들러 호출
                app.root.after(0, lambda error=str(error): handle_start_failure(error))

                return

            # 성공 시 메인 스레드에서 성공 핸들러 호출
            app.root.after(0, lambda response=response: handle_start_success(response))

        # 데몬 스레드로 비동기 네트워크 요청 실행
        threading.Thread(target=send_start_request, daemon=True).start()

    # ==========================================
    # API 요청 성공 콜백 함수: 촬영 중 UI로 전환
    # ==========================================
    def handle_start_success(response):
        show_running()
        app.notify(response.get("message", "촬영을 시작했습니다."), GREEN)

    # ==========================================
    # API 요청 실패 콜백 함수: 대기 상태로 복구 및 에러 알림
    # ==========================================
    def handle_start_failure(message):
        nonlocal capture_state
        capture_state = "idle"
        
        idle_button.configure(
            state=tk.NORMAL,
            text="▶  촬영 시작"
        )

        # 발생한 에러 메시지가 서버 연결 실패 관련인지 확인
        server_unreachable = message.startswith("서버에 연결할 수 없습니다.")

        # 서버 연결 실패 여부에 따라 시스템 상태 업데이트
        if server_unreachable:
            app.state.server_status.set("연결 실패")
        else:
            app.state.server_status.set("연결됨")

            # FTP 저장 모드이면서 에러 메시지에 FTP 관련 내용이 포함된 경우 FTP 연결 상태도 연결 실패로 변경
            if (app.state.storage_mode.get() in ("ftp", "both") and "FTP" in message.upper()):
                app.state.ftp_status.set("연결 실패")

        app.refresh_system_status()
        app.notify(message, RED)

    # ==========================================
    # 촬영 중지 요청 함수
    # ==========================================
    def stop_capture():
        nonlocal capture_state

        # 촬영 중이 아닌 경우 중복 실행 방지
        if capture_state != "running":
            return

        # 이후 작업이 진행되는 동안 중복 클릭 차단
        capture_state = "stopping"
        running_button.configure(
            state=tk.DISABLED,
            text="중지 요청 중..."
        )

        app.notify("라즈베리파이에 촬영 중지 요청을 보내는 중입니다...", BLUE)

        # ==========================================
        # 네트워크 요청 중 GUI가 멈추지 않도록 별도 스레드에서 요청
        # ==========================================
        def send_stop_request():
            try:
                response = request_stop_capture()
            except Exception as error:
                # 에러 발생 시 메인 스레드에서 실패 핸들러 호출
                app.root.after(0, lambda error=str(error): handle_stop_failure(error))
                
                return

            # 성공 시 메인 스레드에서 성공 핸들러 호출
            app.root.after(0, lambda response=response: handle_stop_success(response))

        # 데몬 스레드로 비동기 네트워크 요청 실행
        threading.Thread(target=send_stop_request, daemon=True).start()

    # ==========================================
    # API 요청 성공 콜백 함수: 대기 중 UI로 전환
    # ==========================================
    def handle_stop_success(response):
        show_idle()
        app.notify(response.get("message", "촬영을 중지했습니다."), GREEN)

    # ==========================================
    # API 요청 실패 콜백 함수: 촬영 상태로 복구 및 에러 알림
    # ==========================================
    def handle_stop_failure(message):
        nonlocal capture_state
        capture_state = "running"

        running_button.configure(
            state=tk.NORMAL,
            text="■  촬영 중지"
        )

        app.notify(message, RED)

    # 버튼에 클릭 이벤트 핸들러 바인딩
    idle_button.configure(command=start_capture)
    running_button.configure(command=stop_capture)