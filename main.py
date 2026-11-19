
import threading
import tkinter as tk

from common.enums.system_status import CaptureStatus, ConnectionStatus
from common.state.app_state import AppState
from common.websocket.websocket_client import WebSocketClient
from config import (
    APP_TITLE,
    WINDOW_GEOMETRY,
    WINDOW_MIN_SIZE,
    BG,
    GREEN,
    RED,
    FTP_HOST,
    FTP_PORT,
    FTP_USER,
    FTP_PASSWORD
)

from camera.preview.ui import camera_preview
from camera.preview.ui.camera_preview_manager import CameraPreviewManager
from camera.setting.ui import camera_settings
from capture.control.ui import capture_control
from capture.recent_photos.ui import recent_photos
from capture.setting.ui import capture_settings
from common.ui.common import configure_style
from common.ui.layout import build_header, build_main
from notification.ui import notifications
from storage.mode.ui import storage_mode
from storage.path.ui import save_path
from system.status.ui import system_status

from camera.preview.service.camera_preview_service import CameraPreviewService
from common.service.capture_ui_lock_manager import CaptureUiLockManager
from storage.path.service.ftp_client import test_ftp_connection
from storage.path.service.path_settings_storage import load_path_settings

from capture.control.api.capture_api import stop_capture
from system.status.api.system_api import get_server_status


class CameraManagerApp:
    def __init__(self, root):
        self.root = root
        self.state = AppState(root, load_path_settings())

        self.vcmd = (root.register(self.validate_number), "%P")

        self.notify = lambda message, color=None: None

        self.capture_ui_lock_manager = CaptureUiLockManager()
        self.camera_preview_manager = None

        configure_style()
        build_header(root)
        _, left, center, right = build_main(root)

        system_status.build(left, self)

        camera_preview_ui = camera_preview.build(left, self)
        _, camera_settings_lock = camera_settings.build(
            left,
            self,
            on_camera_config_changed=camera_preview_ui.update_camera_roles
        )

        _, storage_mode_lock = storage_mode.build(left, self)
        _, save_path_lock = save_path.build(left, self)

        _, capture_settings_lock = capture_settings.build(center, self)
        capture_control.build(
            center,
            self,
            before_start_capture=self._before_capture_start
        )

        notifications.build(center, self)
        
        recent_photos.build(right, self)

        preview_service = CameraPreviewService(schedule_callback=self.root.after)
        self.camera_preview_manager = CameraPreviewManager(
            parent=self.root,
            preview_ui=camera_preview_ui,
            preview_service=preview_service,
            on_error=lambda message: self.notify(message, RED)
        )

        self.capture_ui_lock_manager.register("camera_settings", camera_settings_lock)
        self.capture_ui_lock_manager.register("storage_mode", storage_mode_lock)
        self.capture_ui_lock_manager.register("save_path", save_path_lock)
        self.capture_ui_lock_manager.register("capture_settings", capture_settings_lock)

        self.websocket_client = WebSocketClient(
            root=self.root,
            on_status=self._on_websocket_status,
            on_event=self._on_websocket_event
        )
        self.websocket_client.start()

        self._check_initial_server_connection()
        self._check_initial_ftp_connection()

    def _before_capture_start(self, on_complete):
        """촬영 시작 전에 실행 중인 미리보기를 모두 종료합니다.

        Args:
            on_complete (Callable): 미리보기 종료 결과를 전달할 콜백
        """
        self.camera_preview_manager.close_all(on_complete=on_complete)

    def _check_initial_server_connection(self):
        """애플리케이션 시작 시 서버 연결 상태를 확인합니다."""
        def request_status():
            try:
                data = get_server_status()
                error_message = None
            except Exception as error:
                data = None
                error_message = str(error)

            self.root.after(
                0,
                lambda: self._apply_initial_server_status(
                    data,
                    error_message
                )
            )

        threading.Thread(
            target=request_status,
            name="InitialServerConnectionCheck",
            daemon=True
        ).start()

    def _apply_initial_server_status(self, data, error_message):
        """최초 서버 연결 확인 결과를 애플리케이션 상태에 반영합니다.

        Args:
            data (dict | None): 서버 상태 응답 데이터
            error_message (str | None): 연결 오류 메시지
        """
        if error_message is not None:
            self.state.server_status.set(ConnectionStatus.FAILED.value)
            self.refresh_system_status()

            return

        self.state.server_status.set(ConnectionStatus.CONNECTED.value)

        if data.get("capture") == "running":
            self.state.capture_status.set(CaptureStatus.CAPTURING.value)
        else:
            self.state.capture_status.set(CaptureStatus.WAITING.value)

        self.refresh_system_status()

    def _check_initial_ftp_connection(self):
        """애플리케이션 시작 시 FTP 연결 상태를 확인합니다."""
        self.state.ftp_status.set(ConnectionStatus.CONNECTING.value)
        self.refresh_system_status()

        def request_ftp_connection():
            success, message = test_ftp_connection(
                host=FTP_HOST,
                port=FTP_PORT,
                user=FTP_USER,
                password=FTP_PASSWORD,
                remote_path=self.state.ftp_path.get().strip(),
                timeout=5
            )

            self.root.after(
                0,
                lambda: self._apply_initial_ftp_status(
                    success,
                    message
                )
            )

        threading.Thread(
            target=request_ftp_connection,
            name="InitialFTPConnectionCheck",
            daemon=True
        ).start()

    def _apply_initial_ftp_status(self, success, message):
        """최초 FTP 연결 확인 결과를 애플리케이션 상태에 반영합니다.

        Args:
            success (bool): FTP 연결 성공 여부
            message (str): 연결 결과 메시지
        """
        if success:
            self.state.ftp_status.set(ConnectionStatus.CONNECTED.value)
        else:
            self.state.ftp_status.set(ConnectionStatus.FAILED.value)

        self.refresh_system_status()

    def _on_websocket_status(self, status):
        """WebSocket 연결 상태 변경을 처리합니다.

        Args:
            status (str): 변경된 WebSocket 연결 상태
        """
        previous = self.state.websocket_status.get()

        self.state.websocket_status.set(status)
        self.refresh_system_status()

        if status == previous:
            return

        if status == ConnectionStatus.CONNECTED.value:
            self.notify("WebSocket 서버에 연결되었습니다.", GREEN)
        elif status == ConnectionStatus.DISCONNECTED.value:
            self.notify("WebSocket 연결이 끊겼습니다. 재연결을 시도합니다.", RED)
        elif status == ConnectionStatus.FAILED.value:
            self.notify("WebSocket 연결에 실패했습니다. 서버와 네트워크를 확인해 주세요.", RED)

    def _on_websocket_event(self, data):
        """WebSocket으로 수신한 이벤트를 처리합니다.

        Args:
            data (dict): 서버에서 수신한 이벤트 데이터
        """
        if not isinstance(data, dict):
            return

        event_type = data.get("type")

        if event_type == "photo_saved":
            filename = data.get("filename", "")
            view = data.get("view", "")

            if not filename or view not in ("side", "top"):
                return

            preview_data = data.get("preview_data", "")

            if not preview_data:
                print("사진 썸네일 데이터가 없습니다:", filename)

                return

            self.root.after(
                0,
                lambda: recent_photos.update_photo_from_base64(
                    self,
                    view,
                    filename,
                    preview_data
                )
            )

    def close(self):
        """미리보기와 촬영을 정리한 뒤 애플리케이션을 종료합니다."""
        if getattr(self, "_closing", False):
            return

        self._closing = True
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)

        def stop_capture_before_close():
            """서버 촬영 상태를 확인하고 실행 중인 촬영을 중지합니다."""
            try:
                server_status = get_server_status()

                if server_status.get("capture") == "running":
                    stop_capture()
            except Exception as error:
                print("GUI 종료 중 촬영 상태 확인 또는 중지 요청 실패: {}".format(error))

            self.root.after(0, self._finish_close)

        def on_preview_closed(success, message=None):
            """미리보기 종료 결과를 처리합니다.

            Args:
                success (bool): 미리보기 종료 성공 여부
                message (str | None): 미리보기 종료 실패 메시지
            """
            if not success:
                print("GUI 종료 중 미리보기 세션 종료에 실패했습니다: {}".format(message or "알 수 없는 오류"))

            threading.Thread(
                target=stop_capture_before_close,
                name="CaptureStopBeforeCloseThread",
                daemon=False
            ).start()

        try:
            self.camera_preview_manager.close_all(on_complete=on_preview_closed)
        except Exception as error:
            print("GUI 종료 중 미리보기 정리 실패: {}".format(error))

            on_preview_closed(False)

    def _finish_close(self):
        """서버 정리 작업이 끝난 뒤 WebSocket과 GUI를 종료합니다."""
        try:
            self.websocket_client.stop()
        except Exception as error:
            print("GUI 종료 중 WebSocket 연결 종료 실패: {}".format(error))

        self.root.destroy()

    @staticmethod
    def validate_number(value):
        """입력값이 숫자 또는 빈 문자열인지 확인합니다.

        Args:
            value (str): 입력 중인 문자열

        Returns:
            bool: 숫자 또는 빈 문자열이면 True
        """
        return value.isdigit() or value == ""

    def refresh_system_status(self):
        """시스템 상태 UI를 갱신합니다."""
        system_status.refresh(self)


def main():
    root = tk.Tk()
    root.title(APP_TITLE)
    root.geometry(WINDOW_GEOMETRY)
    root.minsize(*WINDOW_MIN_SIZE)
    root.configure(bg=BG)

    app = CameraManagerApp(root)

    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()


if __name__ == "__main__":
    main()
