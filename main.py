import threading
import tkinter as tk
from config import APP_TITLE, WINDOW_GEOMETRY, WINDOW_MIN_SIZE, BG, GREEN, RED
from state import AppState
from ui.common import configure_style
from ui.layout import build_header, build_main
from ui import system_status, server_connection, ftp_settings, save_path
from ui import capture_settings, storage_mode, capture_control
from ui import recent_photos, notifications
from services.websocket_client import WebSocketClient
from services.api_client import get_server_status, stop_capture

# ==========================================
# GUI 애플리케이션 메인 클래스
# ==========================================
class CameraManagerApp:
    def __init__(self, root):
        self.root = root
        self.state = AppState(root)
        # 입력창 숫자 전용 유효성 검증 커맨드 등록(빈 문자열 또는 숫자 허용)
        self.vcmd = (root.register(self.validate_number), "%P")
        # 초기 알림 함수 플레이스홀더
        self.notify = lambda message, color=None: None

        # 촬영 중일 때 입력 제어(잠금/해제) 기능을 수행할 설정 목록
        self.capture_settings_lockers = []

        # 촬영 상태에 따라 등록된 설정 화면들을 일괄적으로 잠그거나 해제하는 람다 함수
        self.set_capture_settings_locked = (
            lambda locked: [
                locker(locked)
                for locker in self.capture_settings_lockers
            ]
        )

        # UI 스타일 및 레이아웃 빌드 영역
        configure_style()
        build_header(root)
        _, left, center, right = build_main(root)

        # 좌측 UI 구성(시스템 상태, 서버 연결, FTP 설정, 저장 경로)
        system_status.build(left, self)
        server_connection.build(left, self)
        ftp_settings.build(left, self)
        save_path.build(left, self)

        # 중앙 UI 구성(촬영 설정, 저장 방식, 촬영 제어)
        capture_settings.build(center, self)
        storage_mode.build(center, self)
        capture_control.build(center, self)

        # 우측 UI 구성(최근 촬영 사진, 알림)
        recent_photos.build(right, self)
        notifications.build(right, self)

        # WebSocket 실시간 알림 클라이언트 초기화 및 시작
        self.websocket_client = WebSocketClient(
            root=self.root,
            on_status=self._on_websocket_status,
            on_event=self._on_websocket_event
        )
        self.websocket_client.start()

    # ==========================================
    # WebSocket 연결 상태 변경 시 호출되는 콜백 함수
    # ==========================================
    def _on_websocket_status(self, status):
        previous = self.state.websocket_status.get()

        self.state.websocket_status.set(status)
        self.refresh_system_status()

        # 상태가 바뀔 때만 알림을 표시
        if status == previous:
            return

        # 연결 상태에 따른 알림 메시지 처리
        if status == "연결됨":
            self.notify("WebSocket 서버에 연결되었습니다.", GREEN)
        elif status == "연결 끊김":
            self.notify("WebSocket 연결이 끊겼습니다. 재연결을 시도합니다.", RED)
        elif status == "연결 실패":
            self.notify("WebSocket 연결에 실패했습니다. 서버와 네트워크를 확인해 주세요.", RED)

    # ==========================================
    # WebSocket을 통해 이벤트 수신 시 호출되는 콜백 함수
    # ==========================================
    def _on_websocket_event(self, data):
        # 수신된 데이터가 딕셔너리 형태가 아닌 경우 무시
        if not isinstance(data, dict):
            return

        event_type = data.get("type")

        # 사진 촬영 완료 이벤트 처리
        if event_type == "photo_saved":
            # 서버 이벤트 데이터에서 사진 파일명과 촬영 뷰 추출
            filename = data.get("filename", "")
            view = data.get("view", "")

            # 사진 파일명이 없거나 유효하지 않은 뷰 이름인 경우 처리 중단
            if not filename or view not in ("side", "top"):
                return

            # 서버에서 전송한 Base64 썸네일 데이터 추출
            preview_data = data.get("preview_data", "")

            # 썸네일 데이터가 누락된 경우 처리 중단
            if not preview_data:
                print("사진 썸네일 데이터가 없습니다:", filename)

                return
            
            # Tkinter GUI 메인 스레드에서 썸네일 UI 갱신
            self.root.after(
                0,
                lambda: recent_photos.update_photo_from_base64(
                    self, view, filename, preview_data
                )
            )

    # ==========================================
    # 애플리케이션 종료 처리 메서드
    # ==========================================
    def close(self):
        # 종료 처리가 이미 진행 중이면 중복 실행 방지
        if getattr(self, "_closing", False):
            return

        self._closing = True

        # GUI 종료 중복 실행을 방지하기 위해 창 닫기 동작 비활성화
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)

        # ==========================================
        # 서버 촬영 상태 확인 및 중지 요청
        # ==========================================
        def stop_capture_before_close():
            try:
                # 서버의 현재 촬영 상태 조회
                server_status = get_server_status()

                # 서버에서 실제 촬영 중인 경우에만 중지 요청
                if server_status.get("capture") == "running":
                    stop_capture()
            except Exception as error:
                # 서버 연결 실패 등으로 중지 요청을 완료하지 못한 경우 기록
                print("GUI 종료 중 촬영 상태 확인 또는 중지 요청 실패: {}".format(error))

        # 백그라운드 스레드에서 서버 촬영 상태 확인 및 중지 처리
        # GUI 창이 닫혀도 중지 요청이 완료될 수 있도록 daemon=False 사용
        threading.Thread(
            target=stop_capture_before_close,
            name="CaptureStopBeforeCloseThread",
            daemon=False
        ).start()

        # WebSocket 연결 종료 요청
        self.websocket_client.stop()

        # 서버 응답을 기다리지 않고 GUI 창 즉시 종료
        self.root.destroy()

    # ==========================================
    # 입력값 유효성 검증 정적 메서드
    # ==========================================
    @staticmethod
    def validate_number(value):
        return value.isdigit() or value == ""
    
    # ==========================================
    # 시스템 상태 UI 갱신 메서드
    # ==========================================
    def refresh_system_status(self):
        system_status.refresh(self)

# ==========================================
# 애플리케이션 main 함수
# ==========================================
def main():
    root = tk.Tk()
    root.title(APP_TITLE)
    root.geometry(WINDOW_GEOMETRY)
    root.minsize(*WINDOW_MIN_SIZE)
    root.configure(bg=BG)

    # 애플리케이션 인스턴스 생성 및 이벤트 루프 실행
    app = CameraManagerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()

if __name__ == "__main__":
    main()