import threading
import tkinter as tk
from config import (
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
from ui.common import create_panel, create_field, create_outline_button

# ==========================================
# FTP 설정 UI 및 기능 함수
# ==========================================
def build(parent, app):
    # '기본값 불러오기' 버튼 클릭 시 호출되는 함수
    def default_load():
        # config에 정의된 기본 FTP 설정값들을 입력 필드에 세팅
        app.state.ftp_host.set(FTP_HOST)
        app.state.ftp_port.set(str(FTP_PORT))
        app.state.ftp_user.set(FTP_USER)
        app.state.ftp_password.set(FTP_PASSWORD)

        app.notify("FTP 기본값을 불러왔습니다.")

    # '연결 테스트' 버튼 클릭 시 호출되는 함수
    def connection_test():
        # 입력된 FTP 설정값 가져오기
        host = app.state.ftp_host.get().strip()
        port_text = app.state.ftp_port.get().strip()
        user = app.state.ftp_user.get().strip()
        password = app.state.ftp_password.get()
        remote_path = FTP_BASE_DIR

        # 필수 입력값 누락 여부 검증
        if not host or not port_text or not user or not password:
            app.notify("FTP 설정 정보를 입력해 주세요.", RED)
            return

        # Port 번호 유효성 검증
        try:
            port = int(port_text)
            if not 1 <= port <= 65535:
                raise ValueError
        except ValueError:
            app.notify("FTP Port는 1~65535 사이의 숫자로 입력해 주세요.", RED)
            return

        # 연결 확인하는 초기 UI 세팅
        app.state.ftp_status.set("연결 확인 중...")
        app.refresh_system_status()
        app.notify("FTP 서버 연결을 확인하고 있습니다...")

        # 백그라운드 스레드에서 실행될 FTP 연결 테스트 작업 함수
        def worker():
            success, message = test_ftp_connection(
                host=host,
                port=port,
                user=user,
                password=password,
                remote_path=remote_path,
                timeout=5
            )

            # 테스트 결과에 따라 UI 상태를 갱신하고 알림을 띄우는 함수
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
    create_field(panel, "FTP Host", app.state.ftp_host)
    create_field(panel, "FTP Port", app.state.ftp_port)
    create_field(panel, "FTP User", app.state.ftp_user)
    create_field(panel, "FTP Password", app.state.ftp_password)

    # '기본값 불러오기' 버튼 담을 프레임 생성
    button_area = tk.Frame(panel, bg=WHITE)
    button_area.pack(fill="x", padx=20, pady=12)

    # '기본값 불러오기' 아웃라인 버튼 생성 및 우측 정렬 배치
    create_outline_button(button_area, "⬇  기본값 불러오기", default_load).pack(side="right")