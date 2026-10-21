import threading
import tkinter as tk
from config import (
    BLUE,
    WHITE,
    GREEN,
    RED,
    FTP_HOST,
    FTP_PORT,
    FTP_USER,
    FTP_PASSWORD,
    FTP_BASE_DIR
)
from services.ftp_client import test_ftp_connection
from services.ftp_validator import validate_ftp_settings
from ui.common import create_panel, create_field, create_outline_button

# ==========================================
# FTP 설정 UI 및 기능 함수
# ==========================================
def build(parent, app):
    # ==========================================
    # '기본값 불러오기' 버튼 클릭 시 호출되는 함수
    # ==========================================
    def default_load():
        # config에 정의된 기본 FTP 설정값들을 입력 필드에 세팅
        app.state.ftp_host.set(FTP_HOST)
        app.state.ftp_port.set(str(FTP_PORT))
        app.state.ftp_user.set(FTP_USER)
        app.state.ftp_password.set(FTP_PASSWORD)

        app.notify("FTP 기본값을 불러왔습니다.")

    # ==========================================
    # '연결 테스트' 버튼 클릭 시 호출되는 함수
    # ==========================================
    def connection_test():
        # 입력된 FTP 설정값 가져오기
        host = app.state.ftp_host.get().strip()
        port_text = app.state.ftp_port.get().strip()
        user = app.state.ftp_user.get().strip()
        password = app.state.ftp_password.get()
        remote_path = FTP_BASE_DIR

        # FTP 설정값 검증
        valid, message, port = validate_ftp_settings(
            host=host,
            port_text=port_text,
            user=user,
            password=password
        )

        if not valid:
            app.notify(message, RED)
            return

        # 연결 확인하는 초기 UI 세팅
        app.state.ftp_status.set("연결 확인 중...")
        app.refresh_system_status()
        app.notify("FTP 서버 연결을 확인하고 있습니다...", BLUE)

        # ==========================================
        # 백그라운드 스레드에서 실행될 FTP 연결 테스트 작업 함수
        # ==========================================
        def worker():
            success, message = test_ftp_connection(
                host=host,
                port=port,
                user=user,
                password=password,
                remote_path=remote_path,
                timeout=5
            )

            # ==========================================
            # 테스트 결과에 따라 UI 상태를 갱신하고 알림을 띄우는 함수
            # ==========================================
            def finish():
                if success:
                    app.state.ftp_status.set("연결됨")
                    app.notify(message, GREEN)
                else:
                    app.state.ftp_status.set("연결 실패")
                    app.notify(message, RED)

                app.refresh_system_status()

            # Tkinter UI 업데이트는 반드시 메인 스레드에서 처리해야 하므로 after 사용
            app.root.after(0, finish)

        # 네트워크 통신 중 UI 멈춤 현상을 방지하기 위한 백그라운드 스레드 생성 및 실행
        threading.Thread(target=worker, daemon=True).start()

    # 상위 패널 생성 및 '연결 테스트' 버튼 연결
    panel = create_panel(parent, "FTP 설정", "🔗  연결 테스트", connection_test)
    panel.pack(fill="x", pady=5)

    # FTP 설정 입력 필드 생성
    host_entry = create_field(panel, "FTP Host", app.state.ftp_host)
    port_entry = create_field(panel, "FTP Port", app.state.ftp_port)
    user_entry = create_field(panel, "FTP User", app.state.ftp_user)
    password_entry = create_field(panel, "FTP Password", app.state.ftp_password)

    # 촬영 중 잠글 FTP 입력창 목록
    ftp_entries = [
        host_entry,
        port_entry,
        user_entry,
        password_entry
    ]

    # '기본값 불러오기' 버튼 담을 프레임 생성
    button_area = tk.Frame(panel, bg=WHITE)
    button_area.pack(fill="x", padx=20, pady=12)

    # '기본값 불러오기' 버튼 생성 및 우측 정렬 배치
    default_button = create_outline_button(button_area, "⬇  기본값 불러오기", default_load)
    default_button.pack(side="right")

    # ==========================================
    # 촬영 중 FTP 설정 잠금 및 해제 함수
    # ==========================================
    def set_ftp_settings_locked(locked):
        # 잠김 상태(locked)에 따라 입력창 상태를 비활성화(disabled) 또는 활성화(normal)로 설정
        new_state = "disabled" if locked else "normal"

        # FTP 입력창 4개 상태 일괄 변경
        for entry in ftp_entries:
            entry.configure(state=new_state)

        # '기본값 불러오기' 버튼 상태 변경
        default_button.configure(state=new_state)

    # 촬영 제어 화면에서 호출할 수 있도록 등록
    app.capture_settings_lockers.append(
        set_ftp_settings_locked
    )