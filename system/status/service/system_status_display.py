
from common.enums.system_status import (CaptureStatus, ConnectionStatus)
from config import GREEN, GRAY, RED

def build_system_status_display_items(app_state):
    """시스템 상태 UI에 표시할 데이터를 구성하여 반환합니다.

    Args:
        app_state (AppState): 애플리케이션 상태 객체

    Returns:
        list: 상태 항목의 이름, 상태값, 표시 색상 목록
    """
    statuses = [
        ("서버 상태", app_state.server_status.get()),
        ("WS 상태", app_state.websocket_status.get()),
        ("촬영 상태", app_state.capture_status.get()),
        ("FTP 상태", app_state.ftp_status.get())
    ]

    return [
        (label, value, get_status_color(value))
        for label, value in statuses
    ]


def get_status_color(status):
    """시스템 상태값에 해당하는 표시 색상을 반환합니다.

    Args:
        status (str): 색상을 확인할 시스템 상태값

    Returns:
        str: 상태에 해당하는 색상 코드
    """
    if status in (ConnectionStatus.CONNECTED.value, CaptureStatus.CAPTURING.value):
        return GREEN

    if status == ConnectionStatus.FAILED.value:
        return RED

    return GRAY
