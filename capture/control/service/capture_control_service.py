
import threading

from config import GREEN, RED, BLUE, FTP_HOST, FTP_PORT, FTP_USER, FTP_PASSWORD

from capture.control.service.capture_start_validator import validate_capture_start_settings

from capture.control.api.capture_api import (
    start_capture as request_start_capture,
    stop_capture as request_stop_capture
)


class CaptureControlService:
    """촬영 시작 및 중지 요청과 처리 흐름을 관리합니다.

    Args:
        schedule_callback (Callable): 메인 UI 스레드에서 콜백을 실행하는 함수
        on_state_change (Callable): 촬영 상태 변경 콜백
        on_status_change (Callable): 시스템 상태 변경 콜백
        on_notification (Callable): 알림 표시 콜백
        before_start_capture (Callable, optional): 촬영 시작 전 실행할 작업
    """

    def __init__(self, schedule_callback, on_state_change, on_status_change, on_notification, before_start_capture=None):
        self._schedule_callback = schedule_callback
        self._on_state_change = on_state_change
        self._on_status_change = on_status_change
        self._on_notification = on_notification
        self._before_start_capture = before_start_capture

        self._capture_state = "idle"
        self._state_lock = threading.Lock()

    def start_capture(self, settings):
        """촬영 설정을 검증하고 서버에 촬영 시작을 요청합니다.

        Args:
            settings (dict): 촬영 시간, 간격, 저장 방식 및 저장 경로 설정
        """
        with self._state_lock:
            if self._capture_state != "idle":
                return

            self._capture_state = "starting"

        self._dispatch(self._on_state_change, "starting")

        valid, message = validate_capture_start_settings(
            hour_text=settings["hour_text"],
            minute_text=settings["minute_text"],
            second_text=settings["second_text"],
            interval_text=settings["interval_text"],
            storage_mode=settings["storage_mode"],
            local_path=settings["local_path"],
            ftp_path=settings["ftp_path"]
        )

        if not valid:
            self._change_state("idle")
            self._notify(message, RED)

            return

        payload = self._build_capture_payload(settings)

        if self._before_start_capture is None:
            self._start_request(payload)

            return

        self._notify("미리보기 종료 후 촬영을 시작합니다...", BLUE)

        callback_lock = threading.Lock()
        callback_completed = False

        def on_preview_closed(success):
            """미리보기 종료 결과에 따라 촬영 시작을 진행합니다.

            Args:
                success (bool): 미리보기 종료 성공 여부
            """
            nonlocal callback_completed

            with callback_lock:
                if callback_completed:
                    return

                callback_completed = True

            if not success:
                self._change_state("idle")
                self._notify("미리보기를 종료하지 못해 촬영을 시작하지 않았습니다.", RED)

                return

            self._start_request(payload)

        try:
            self._before_start_capture(on_preview_closed)
        except Exception as error:
            self._change_state("idle")
            self._notify("촬영 시작 전 미리보기 정리 중 오류가 발생했습니다: {}".format(error), RED)

    def stop_capture(self):
        """서버에 촬영 중지 요청을 전송합니다."""
        with self._state_lock:
            if self._capture_state != "running":
                return

            self._capture_state = "stopping"

        self._dispatch(self._on_state_change, "stopping")

        self._notify("서버에 촬영 중지 요청을 보내는 중입니다...", BLUE)

        threading.Thread(
            target=self._send_stop_request,
            daemon=True
        ).start()

    def _start_request(self, payload):
        """촬영 시작 API 요청을 백그라운드에서 실행합니다.

        Args:
            payload (dict): 서버에 전달할 촬영 설정
        """
        self._notify("서버에 촬영 시작 요청을 보내는 중입니다...", BLUE)

        threading.Thread(
            target=self._send_start_request,
            args=(payload,),
            daemon=True
        ).start()

    @staticmethod
    def _build_capture_payload(settings):
        """촬영 설정을 서버 요청 데이터로 구성합니다.

        Args:
            settings (dict): 촬영 설정값

        Returns:
            dict: 서버에 전달할 촬영 시작 요청 데이터
        """
        storage_mode = settings["storage_mode"]

        payload = {
            "start_time": "{}:{}:{}".format(
                settings["hour_text"].strip(),
                settings["minute_text"].strip(),
                settings["second_text"].strip()
            ),
            "interval_minutes": int(settings["interval_text"].strip()),
            "storage_mode": storage_mode
        }

        if storage_mode in ("local", "both"):
            payload["local_path"] = settings["local_path"].strip()

        if storage_mode in ("ftp", "both"):
            payload["ftp"] = {
                "host": FTP_HOST,
                "port": int(FTP_PORT),
                "user": FTP_USER,
                "password": FTP_PASSWORD,
                "base_dir": settings["ftp_path"].strip()
            }

        return payload

    def _send_start_request(self, payload):
        """백그라운드 스레드에서 촬영 시작 API를 요청합니다.

        Args:
            payload (dict): 서버에 전달할 촬영 설정
        """
        try:
            response = request_start_capture(payload)
        except Exception as error:
            self._dispatch(self._handle_start_failure, str(error))

            return

        self._dispatch(self._handle_start_success, response)

    def _send_stop_request(self):
        """백그라운드 스레드에서 촬영 중지 API를 요청합니다."""
        try:
            response = request_stop_capture()
        except Exception as error:
            self._dispatch(self._handle_stop_failure, str(error))

            return

        self._dispatch(self._handle_stop_success, response)

    def _handle_start_success(self, response):
        """촬영 시작 요청 성공 결과를 처리합니다.

        Args:
            response (dict): 서버 응답 데이터
        """
        self._change_state("running")

        status_updates = {
            "server_status": "연결 성공",
            "capture_status": "촬영 중"
        }

        if response and response.get("success"):
            self._notify(response.get("message", "촬영을 시작했습니다."), GREEN)
        else:
            self._notify("촬영을 시작했습니다.", GREEN)

        self._on_status_change(status_updates)

    def _handle_start_failure(self, message):
        """촬영 시작 요청 실패 결과를 처리합니다.

        Args:
            message (str): 요청 실패 메시지
        """
        self._change_state("idle")

        status_updates = {}

        server_unreachable = message.startswith("서버에 연결할 수 없습니다.")

        if server_unreachable:
            status_updates["server_status"] = "연결 실패"
        else:
            status_updates["server_status"] = "연결 성공"

            if "FTP" in message.upper():
                status_updates["ftp_status"] = "연결 실패"

        if status_updates:
            self._on_status_change(status_updates)

        self._notify(message, RED)

    def _handle_stop_success(self, response):
        """촬영 중지 요청 성공 결과를 처리합니다.

        Args:
            response (dict): 서버 응답 데이터
        """
        self._change_state("idle")

        self._on_status_change({"capture_status": "대기 중"})

        self._notify(response.get("message", "촬영을 중지했습니다."), GREEN)

    def _handle_stop_failure(self, message):
        """촬영 중지 요청 실패 결과를 처리합니다.

        Args:
            message (str): 요청 실패 메시지
        """
        self._change_state("running")
        self._notify(message, RED)

    def _change_state(self, state):
        """내부 촬영 상태를 변경하고 UI에 알립니다.

        Args:
            state (str): 변경할 촬영 상태
        """
        with self._state_lock:
            self._capture_state = state

        self._dispatch(self._on_state_change, state)

    def _notify(self, message, color=None):
        """알림 콜백을 메인 UI 스레드에서 실행합니다.

        Args:
            message (str): 표시할 알림 메시지
            color (str, optional): 알림 색상
        """
        self._dispatch(self._on_notification, message, color)

    def _dispatch(self, callback, *args):
        """콜백을 메인 UI 스레드에 예약합니다.

        Args:
            callback (Callable): 실행할 콜백 함수
            *args: 콜백에 전달할 인수
        """
        self._schedule_callback(0, lambda: callback(*args))
