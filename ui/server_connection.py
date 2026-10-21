import threading
import tkinter as tk
from config import WHITE, BLUE, BLUE_LIGHT, RED, GREEN
from services.api_client import get_server_status
from ui.common import create_panel

# ==========================================
# 서버 연결 UI 및 기능 함수
# ==========================================
def build(parent, app):
    # ==========================================
    # '연결 테스트' 버튼 클릭 시 호출되는 함수
    # ==========================================
    def connection_test():
        # 연결 확인하는 초기 UI 세팅
        app.state.server_status.set("연결 확인 중...")
        app.refresh_system_status()

        app.notify("라즈베리파이 서버 연결을 확인하고 있습니다...", BLUE)

        # ==========================================
        # 백그라운드 스레드에서 서버로 상태 요청을 보내는 함수
        # ==========================================
        def request_status():
            try:
                data = get_server_status()
                error_message = None
            except Exception as error:
                data = None
                error_message = str(error)

            # Tkinter UI 업데이트는 반드시 메인 스레드에서 처리해야 하므로 after 사용
            app.root.after(0, lambda: show_result(data, error_message))

        # ==========================================
        # 요청 결과에 따라 UI 상태를 갱신하고 알림을 띄우는 함수(메인 스레드 실행)
        # ==========================================
        def show_result(data, error_message):
            if error_message is not None:
                app.state.server_status.set("연결 실패")
                app.refresh_system_status()

                app.notify("서버 연결 실패: {}".format(error_message), RED)

                return

            app.state.server_status.set("연결됨")

            if data.get("capture") == "running":
                app.state.capture_status.set("촬영 중")
                capture_text = "촬영 중"
            else:
                app.state.capture_status.set("대기 중")
                capture_text = "대기 중"

            app.refresh_system_status()

            app.notify("서버 연결 성공", GREEN)
            app.notify("촬영 상태: {}".format(capture_text))

        # API 통신 중 UI 멈춤 현상을 방지하기 위한 백그라운드 스레드 생성 및 실행
        threading.Thread(
            target=request_status,
            daemon=True
        ).start()

    # 상위 패널 생성 및 '연결 테스트' 버튼 연결
    panel = create_panel(parent, "서버 연결", "🔗  연결 테스트", connection_test)
    panel.pack(fill="x", pady=5)

    # 하단 안내 문구를 담을 바디 프레임 생성
    body = tk.Frame(panel, bg=WHITE)
    body.pack(fill="x", padx=20, pady=12)

    # IP 자동 설정 관련 고정 안내 문구 라벨 생성
    tk.Label(
        body,
        text=(
            "ⓘ  설정된 IP 주소와 포트로 자동 연결됩니다.\n"
            "    사용자가 직접 수정할 수 없습니다."
        ),
        bg=BLUE_LIGHT,
        fg=BLUE,
        justify="left",
        font=("Malgun Gothic", 8),
        padx=10,
        pady=9
    ).pack(fill="x")