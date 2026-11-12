from enum import Enum


class ConnectionStatus(Enum):
    """서버, FTP, WebSocket 상태를 관리합니다."""

    WAITING = "대기 중"
    CONNECTING = "연결 중"
    CONNECTED = "연결 성공"
    DISCONNECTED = "연결 실패"


class CaptureStatus(Enum):
    """촬영 상태를 관리합니다."""

    WAITING = "대기 중"
    CAPTURING = "촬영 중"