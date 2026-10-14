import tkinter as tk
from config import APP_TITLE, WINDOW_GEOMETRY, WINDOW_MIN_SIZE, BG
from state import AppState
from ui.common import configure_style
from ui.layout import build_header, build_main
from ui import system_status, server_connection, ftp_settings, save_path
from ui import capture_settings, storage_mode, capture_control
from ui import recent_photos, notifications

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

    # 입력값 유효성 검증 정적 메서드
    @staticmethod
    def validate_number(value):
        return value.isdigit() or value == ""

    # 시스템 상태 UI 갱신 메서드
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
    CameraManagerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()