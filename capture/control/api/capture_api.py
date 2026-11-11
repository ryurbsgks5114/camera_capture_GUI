
from common.api.http_client import request_json


def start_capture(payload):
    """촬영 시작을 서버에 요청합니다.

    Args:
        payload (dict): 촬영 시작 요청 데이터

    Returns:
        dict: 서버 응답 데이터

    Raises:
        RuntimeError: 촬영 시작 요청에 실패한 경우
    """
    status_code, data = request_json(
        "/start",
        method="POST",
        payload=payload
    )

    if status_code < 200 or status_code >= 300 or not data.get("success", False):
        raise RuntimeError(
            data.get("message", "촬영 시작 요청에 실패했습니다.")
        )

    return data


def stop_capture():
    """촬영 중지를 서버에 요청합니다.

    Returns:
        dict: 서버 응답 데이터

    Raises:
        RuntimeError: 촬영 중지 요청에 실패한 경우
    """
    status_code, data = request_json(
        "/stop",
        method="POST"
    )

    if status_code < 200 or status_code >= 300 or not data.get("success", False):
        raise RuntimeError("촬영 중지 요청에 실패했습니다.")

    return data
