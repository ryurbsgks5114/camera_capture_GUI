
import threading

from camera.preview.api.preview_api import (start_preview, stop_preview, get_preview_frame)


class CameraPreviewService:
    """카메라 미리보기 실행과 프레임 조회를 관리합니다."""
    def __init__(self, schedule_callback, frame_interval_ms=200):
        """미리보기 서비스에 필요한 실행 환경을 초기화합니다.

        Args:
            schedule_callback (callable): 지연 실행 및 콜백 전달 함수
            frame_interval_ms (int): 프레임 조회 간격(ms)
        """
        self._schedule_callback = schedule_callback
        self._frame_interval_ms = frame_interval_ms

        self._preview_running = False
        self._preview_requesting = False
        self._frame_error_reported = False

    def start_preview(self, on_success, on_error, on_frames, on_frame_error):
        """카메라 미리보기를 시작합니다.

        Args:
            on_success (callable): 시작 성공 시 실행할 콜백
            on_error (callable): 시작 실패 시 실행할 콜백
            on_frames (callable): 프레임 조회 성공 시 실행할 콜백
            on_frame_error (callable): 프레임 조회 실패 시 실행할 콜백

        Returns:
            bool: 시작 요청을 실행했는지 여부
        """
        if self._preview_running:
            return False

        def worker():
            try:
                response = start_preview()
            except Exception as error:
                self._dispatch(on_error, str(error))

                return

            self._preview_running = True
            self._frame_error_reported = False

            self._dispatch(on_success, response)

            self._schedule_frame_request(on_frames, on_frame_error)

        threading.Thread(
            target=worker,
            name="CameraPreviewStartThread",
            daemon=True,
        ).start()

        return True

    def stop_preview(self, on_success, on_error):
        """카메라 미리보기를 중지합니다.

        Args:
            on_success (callable): 중지 성공 시 실행할 콜백
            on_error (callable): 중지 실패 시 실행할 콜백

        Returns:
            bool: 중지 요청을 실행했는지 여부
        """
        if not self._preview_running:
            return False

        self._preview_running = False

        def worker():
            try:
                response = stop_preview()
            except Exception as error:
                self._preview_running = True
                self._dispatch(on_error, str(error))

                return

            self._dispatch(on_success, response)

        threading.Thread(
            target=worker,
            name="CameraPreviewStopThread",
            daemon=True,
        ).start()

        return True

    def _schedule_frame_request(self, on_frames, on_frame_error):
        """다음 프레임 조회 작업을 예약합니다.

        Args:
            on_frames (callable): 프레임 조회 성공 시 실행할 콜백
            on_frame_error (callable): 프레임 조회 실패 시 실행할 콜백
        """
        if not self._preview_running:
            return

        self._schedule_callback(
            self._frame_interval_ms,
            lambda: self._fetch_preview_frames(
                on_frames,
                on_frame_error,
            ),
        )

    def _fetch_preview_frames(self, on_frames, on_frame_error):
        """Side와 Top 카메라의 최신 프레임을 조회합니다.

        Args:
            on_frames (callable): 프레임 조회 성공 시 실행할 콜백
            on_frame_error (callable): 프레임 조회 실패 시 실행할 콜백
        """
        if not self._preview_running or self._preview_requesting:
            return

        self._preview_requesting = True

        def worker():
            frames = {}
            error_message = None

            try:
                frames["side"] = get_preview_frame("side")
                frames["top"] = get_preview_frame("top")
            except Exception as error:
                error_message = str(error)
            finally:
                self._preview_requesting = False

            if not self._preview_running:
                return

            if error_message:
                if not self._frame_error_reported:
                    self._frame_error_reported = True
                    self._dispatch(on_frame_error, error_message)
            else:
                self._frame_error_reported = False
                self._dispatch(on_frames, frames)

            self._schedule_frame_request(on_frames, on_frame_error)

        threading.Thread(
            target=worker,
            name="CameraPreviewFrameThread",
            daemon=True,
        ).start()

    def _dispatch(self, callback, *args):
        """콜백을 지정된 실행 환경에서 처리하도록 예약합니다.

        Args:
            callback (callable): 실행할 콜백
            *args: 콜백에 전달할 인수
        """
        try:
            self._schedule_callback(0, lambda: callback(*args))
        except (RuntimeError, ValueError):
            pass
