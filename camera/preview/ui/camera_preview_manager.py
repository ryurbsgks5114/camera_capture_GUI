
from camera.preview.ui.preview_window import PreviewWindow


class CameraPreviewManager:
    """카메라 미리보기 창과 서버 세션의 생명주기를 관리합니다."""

    SESSION_STOPPED = "stopped"
    SESSION_STARTING = "starting"
    SESSION_RUNNING = "running"
    SESSION_STOPPING = "stopping"

    VALID_VIEWS = ("side", "top")

    def __init__(
        self,
        parent,
        preview_ui,
        preview_service,
        on_error=None
    ):
        """미리보기 관리자에 필요한 객체를 초기화합니다.

        Args:
            parent (tk.Widget): 미리보기 창의 부모 위젯
            preview_ui (CameraPreviewUI): 미리보기 패널 UI
            preview_service (CameraPreviewService): 미리보기 서비스
            on_error (callable, optional): 오류 발생 시 호출할 콜백
        """
        self._parent = parent
        self._preview_ui = preview_ui
        self._preview_service = preview_service
        self._on_error = on_error

        self._windows = {}

        self._session_state = self.SESSION_STOPPED

        self._stop_after_start = False
        self._restart_after_stop = False

        self._close_callbacks = []

        self._preview_service.set_frame_callbacks(
            self._handle_frames,
            self._handle_frame_error
        )

        self._preview_ui.set_preview_handler(
            self.open_preview
        )

    def open_preview(self, view):
        """선택한 카메라의 미리보기 창을 엽니다.

        Args:
            view (str): 카메라 구분값 (side 또는 top)
        """
        if view not in self.VALID_VIEWS:
            self._report_error("잘못된 카메라 구분입니다.")
            return

        existing_window = self._windows.get(view)

        if existing_window is not None:
            try:
                if existing_window._window.winfo_exists():
                    existing_window._window.lift()
                    return
            except Exception:
                self._windows.pop(view, None)

        try:
            preview_window = PreviewWindow(
                self._parent,
                view,
                self.close_preview
            )
        except Exception as error:
            self._report_error(
                "미리보기 창을 열지 못했습니다: {}".format(error)
            )
            return

        self._windows[view] = preview_window

        self._update_active_views()

        if self._session_state == self.SESSION_STOPPED:
            self._start_session()

        elif self._session_state == self.SESSION_STARTING:
            self._stop_after_start = False

        elif self._session_state == self.SESSION_STOPPING:
            self._restart_after_stop = True

    def close_preview(self, view):
        """선택한 미리보기 창을 닫습니다.

        Args:
            view (str): 닫을 카메라 구분값
        """
        preview_window = self._windows.pop(view, None)

        if preview_window is None:
            return

        preview_window.close()

        self._update_active_views()

        self._stop_session_if_unused()

    def close_all(self, on_complete=None):
        """모든 미리보기 창을 닫고 서버 세션 종료를 요청합니다.

        Args:
            on_complete (callable, optional):
                종료 완료 시 실행할 콜백.
                성공 여부와 오류 메시지를 전달합니다.
        """
        if on_complete is not None:
            self._close_callbacks.append(on_complete)

        windows = list(self._windows.values())
        self._windows.clear()

        for preview_window in windows:
            preview_window.close()

        self._update_active_views()

        if self._session_state == self.SESSION_STOPPED:
            self._complete_close_callbacks(True, None)

        elif self._session_state == self.SESSION_STARTING:
            self._stop_after_start = True

        elif self._session_state == self.SESSION_RUNNING:
            self._stop_session()

        elif self._session_state == self.SESSION_STOPPING:
            self._stop_after_start = True

    def _start_session(self):
        """서버 미리보기 세션을 시작합니다."""
        if self._session_state != self.SESSION_STOPPED:
            return

        if not self._windows:
            return

        self._session_state = self.SESSION_STARTING
        self._stop_after_start = False

        active_views = list(self._windows.keys())

        started = self._preview_service.start_preview(
            on_success=self._handle_start_success,
            on_error=self._handle_start_error,
            on_frames=self._handle_frames,
            on_frame_error=self._handle_frame_error,
            active_views=active_views
        )

        if not started:
            self._session_state = self.SESSION_STOPPED

            self._report_error(
                "미리보기 시작 요청을 실행하지 못했습니다."
            )

    def _handle_start_success(self, response):
        """서버 미리보기 세션 시작 결과를 처리합니다.

        Args:
            response (dict): 서버 응답 데이터
        """
        if self._session_state != self.SESSION_STARTING:
            return

        self._session_state = self.SESSION_RUNNING

        self._update_active_views()

        if self._stop_after_start or not self._windows:
            self._stop_after_start = False
            self._stop_session()

    def _handle_start_error(self, message):
        """서버 미리보기 세션 시작 실패를 처리합니다.

        Args:
            message (str): 오류 메시지
        """
        self._session_state = self.SESSION_STOPPED
        self._stop_after_start = False

        self._report_error(
            "카메라 미리보기를 시작하지 못했습니다: {}".format(message)
        )

        self._complete_close_callbacks(
            False,
            message
        )

    def _stop_session_if_unused(self):
        """열려 있는 미리보기 창이 없으면 세션 종료를 요청합니다."""
        if self._windows:
            return

        if self._session_state == self.SESSION_STARTING:
            self._stop_after_start = True
            return

        if self._session_state == self.SESSION_RUNNING:
            self._stop_session()

    def _stop_session(self):
        """서버 미리보기 세션 종료를 요청합니다."""
        if self._session_state != self.SESSION_RUNNING:
            return

        self._session_state = self.SESSION_STOPPING
        self._restart_after_stop = bool(self._windows)

        stopped = self._preview_service.stop_preview(
            on_success=self._handle_stop_success,
            on_error=self._handle_stop_error
        )

        if not stopped:
            self._session_state = self.SESSION_RUNNING

            self._report_error(
                "미리보기 종료 요청을 실행하지 못했습니다."
            )

            self._complete_close_callbacks(
                False,
                "미리보기 종료 요청을 실행하지 못했습니다."
            )

    def _handle_stop_success(self, response):
        """서버 미리보기 세션 종료 결과를 처리합니다.

        Args:
            response (dict): 서버 응답 데이터
        """
        if self._session_state != self.SESSION_STOPPING:
            return

        self._session_state = self.SESSION_STOPPED

        self._complete_close_callbacks(
            True,
            None
        )

        should_restart = (
            self._restart_after_stop
            and bool(self._windows)
        )

        self._restart_after_stop = False

        if should_restart:
            self._start_session()

    def _handle_stop_error(self, message):
        """서버 미리보기 세션 종료 실패를 처리합니다.

        Args:
            message (str): 오류 메시지
        """
        self._session_state = self.SESSION_RUNNING

        self._restart_after_stop = False

        self._update_active_views()

        self._report_error(
            "카메라 미리보기를 종료하지 못했습니다: {}".format(message)
        )

        self._complete_close_callbacks(
            False,
            message
        )

    def _handle_frames(self, frames):
        """조회된 카메라 프레임을 해당 미리보기 창에 전달합니다.

        Args:
            frames (dict): 카메라별 JPEG 이미지 데이터
        """
        if self._session_state != self.SESSION_RUNNING:
            return

        for view, frame_data in frames.items():
            preview_window = self._windows.get(view)

            if preview_window is None:
                continue

            preview_window.update_frame(frame_data)

    def _handle_frame_error(self, message):
        """프레임 조회 실패를 처리합니다.

        Args:
            message (str): 오류 메시지
        """
        if self._session_state != self.SESSION_RUNNING:
            return

        self._report_error(
            "미리보기 프레임 조회에 실패했습니다: {}".format(message)
        )

    def _update_active_views(self):
        """현재 열려 있는 창에 해당하는 활성 카메라를 서비스에 전달합니다."""
        active_views = list(self._windows.keys())

        self._preview_service.set_active_views(
            active_views
        )

    def _complete_close_callbacks(self, success, message):
        """대기 중인 모든 창 종료 완료 콜백을 실행합니다.

        Args:
            success (bool): 서버 세션 종료 성공 여부
            message (str | None): 오류 메시지
        """
        callbacks = self._close_callbacks
        self._close_callbacks = []

        for callback in callbacks:
            try:
                callback(success, message)
            except Exception as error:
                self._report_error(
                    "미리보기 종료 콜백 실행 실패: {}".format(error)
                )

    def _report_error(self, message):
        """외부 오류 처리 콜백을 실행합니다.

        Args:
            message (str): 오류 메시지
        """
        if self._on_error is None:
            return

        self._on_error(message)
