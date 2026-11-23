
import tkinter as tk

from common.enums.system_status import (
    CaptureStatus,
    ConnectionStatus
)
from config import (
    DEFAULT_STORAGE_MODE,
    DEFAULT_INTERVAL_MINUTES,
    DEFAULT_START_HOUR,
    DEFAULT_START_MINUTE,
    DEFAULT_START_SECOND
)


class AppState:
    """애플리케이션 전체에서 공유하는 상태 변수를 관리합니다.

    Args:
        root (tk.Tk): 애플리케이션의 최상위 Tkinter 객체
        path_settings (dict): 로컬 및 FTP 저장 경로 설정
    """
    def __init__(self, root, path_settings):
        self.root = root

        # 시스템 상태 관련 변수
        self.server_status = tk.StringVar(value=ConnectionStatus.WAITING.value)
        self.capture_status = tk.StringVar(value=CaptureStatus.WAITING.value)
        self.ftp_status = tk.StringVar(value=ConnectionStatus.WAITING.value)
        self.websocket_status = tk.StringVar(value=ConnectionStatus.CONNECTING.value)

        # 촬영 설정 관련 변수
        self.hour_var = tk.StringVar(value=DEFAULT_START_HOUR)
        self.minute_var = tk.StringVar(value=DEFAULT_START_MINUTE)
        self.second_var = tk.StringVar(value=DEFAULT_START_SECOND)
        self.interval_var = tk.StringVar(value=DEFAULT_INTERVAL_MINUTES)

        # 저장 경로 설정 관련 변수
        self.local_path = tk.StringVar(value=path_settings["local_path"])
        self.ftp_path = tk.StringVar(value=path_settings["ftp_path"])

        # 저장 방식 관련 변수
        self.storage_mode = tk.StringVar(value=DEFAULT_STORAGE_MODE)
