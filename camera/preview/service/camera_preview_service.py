
import threading

from camera.preview.api.preview_api import start_preview, stop_preview, get_preview_frame


class CameraPreviewService:
    """카메라 미리보기 세션과 활성 카메라 프레임 조회를 관리합니다."""
    VALID_VIEWS = ("side", "top")

    def __init__(self, schedule_callback, frame_interval_ms=200):
        """미리보기 서비스에 필요한 실행 환경을 초기화합니다.

        Args:
            schedule_callback (callable): 지연 실행 및 콜백 전달 함수
            frame_interval_ms (int): 프레임 조회 간격(ms)
        """
        self._schedule_callback = schedule_callback
        self._frame_interval_ms = frame_interval_ms

        self._lock = threading.RLock()

        self._preview_running = False
        self._preview_starting = False
        self._preview_requesting = False

        self._active_views = set()

        self._generation = 0
        self._frame_error_reported = False

        self._frame_request_finished = threading.Event()
        self._frame_request_finished.set()

    def set_active_views(self, views):
        """현재 미리보기를 표시할 카메라 목록을 설정합니다.

        Args:
            views (iterable): 활성화할 카메라 구분값 목록
        """
        active_views = set(views)

        invalid_views = active_views.difference(self.VALID_VIEWS)

        if invalid_views:
            raise ValueError("잘못된 카메라 구분값이 포함되어 있습니다.")

        with self._lock:
            previous_views = self._active_views
            self._active_views = active_views

            should_schedule = (
                self._preview_running
                and not previous_views
                and bool(active_views)
            )

            generation = self._generation

        if should_schedule:
            self._schedule_frame_request(generation)

    def start_preview(self, on_success, on_error, on_frames, on_frame_error, active_views=None):
        """카메라 미리보기를 시작합니다.

        Args:
            on_success (callable): 시작 성공 시 실행할 콜백
            on_error (callable): 시작 실패 시 실행할 콜백
            on_frames (callable): 프레임 조회 성공 시 실행할 콜백
            on_frame_error (callable): 프레임 조회 실패 시 실행할 콜백
            active_views (iterable, optional): 활성화할 카메라 목록

        Returns:
            bool: 시작 요청을 실행했는지 여부
        """
        with self._lock:
            if self._preview_running or self._preview_starting:
                return False

            if active_views is not None:
                self.set_active_views(active_views)
            elif not self._active_views:
                self._active_views = set(self.VALID_VIEWS)

            self._preview_starting = True
            self._generation += 1

            generation = self._generation

        def worker():
            try:
                response = start_preview()
            except Exception as error:
                with self._lock:
                    if generation == self._generation:
                        self._preview_starting = False

                self._dispatch(on_error, str(error))

                return

            with self._lock:
                if generation != self._generation:
                    return

                self._preview_starting = False
                self._preview_running = True
                self._frame_error_reported = False

            self._dispatch(on_success, response)

            self._schedule_frame_request(generation)

        threading.Thread(
            target=worker,
            name="CameraPreviewStartThread",
            daemon=True
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
        with self._lock:
            if not self._preview_running:
                return False

            self._preview_running = False
            self._generation += 1

            generation = self._generation
            previous_views = set(self._active_views)

            self._active_views.clear()

        def worker():
            self._frame_request_finished.wait()

            try:
                response = stop_preview()
            except Exception as error:
                with self._lock:
                    if generation == self._generation:
                        self._preview_running = True
                        self._active_views = previous_views

                self._dispatch(on_error, str(error))

                if previous_views:
                    self._schedule_frame_request(generation)

                return

            self._dispatch(on_success, response)

        threading.Thread(
            target=worker,
            name="CameraPreviewStopThread",
            daemon=True
        ).start()

        return True

    def _schedule_frame_request(self, generation):
        """다음 프레임 조회 작업을 예약합니다.

        Args:
            generation (int): 현재 미리보기 실행 세대 번호
        """
        with self._lock:
            if not self._preview_running:
                return

            if generation != self._generation:
                return

            if not self._active_views:
                return

        self._schedule_callback(
            self._frame_interval_ms,
            lambda: self._fetch_preview_frames(generation)
        )

    def _fetch_preview_frames(self, generation):
        """활성화된 카메라의 최신 프레임을 조회합니다.

        Args:
            generation (int): 현재 미리보기 실행 세대 번호
        """
        with self._lock:
            if not self._preview_running:
                return

            if generation != self._generation:
                return

            if self._preview_requesting:
                return

            active_views = set(self._active_views)

            if not active_views:
                return

            self._preview_requesting = True
            self._frame_request_finished.clear()

        def worker():
            frames = {}
            errors = []

            try:
                for view in self.VALID_VIEWS:
                    if view not in active_views:
                        continue

                    with self._lock:
                        if (not self._preview_running or generation != self._generation):
                            return

                    try:
                        frame_data = get_preview_frame(view)

                        if frame_data:
                            frames[view] = frame_data
                    except Exception as error:
                        errors.append("{} 카메라: {}".format(view, error))
            finally:
                with self._lock:
                    self._preview_requesting = False
                    self._frame_request_finished.set()

            with self._lock:
                if (not self._preview_running or generation != self._generation):
                    return

            if frames:
                self._dispatch(self._on_frames, frames)

            if errors:
                if not self._frame_error_reported:
                    self._frame_error_reported = True

                    self._dispatch(self._on_frame_error, "\n".join(errors))
            else:
                self._frame_error_reported = False

            self._schedule_frame_request(generation)

        threading.Thread(
            target=worker,
            name="CameraPreviewFrameThread",
            daemon=True
        ).start()

    def set_frame_callbacks(self, on_frames, on_frame_error):
        """프레임 조회 결과를 전달할 콜백을 설정합니다.

        Args:
            on_frames (callable): 프레임 조회 성공 시 실행할 콜백
            on_frame_error (callable): 프레임 조회 실패 시 실행할 콜백
        """
        self._on_frames = on_frames
        self._on_frame_error = on_frame_error

    def _dispatch(self, callback, *args):
        """콜백을 지정된 실행 환경에서 처리하도록 예약합니다.

        Args:
            callback (callable): 실행할 콜백
            *args: 콜백에 전달할 인수
        """
        if callback is None:
            return

        try:
            self._schedule_callback(0, lambda: callback(*args)
            )
        except (RuntimeError, ValueError):
            pass
