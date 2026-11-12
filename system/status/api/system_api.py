
from common.api.http_client import request_json


def get_server_status():
    """서버 상태를 조회합니다.

    Returns:
        dict: 서버 상태 정보

    Raises:
        RuntimeError: 서버 상태 조회에 실패한 경우
    """
    
    status_code, data = request_json("/status", method="GET")

    if status_code != 200:
        raise RuntimeError("서버 상태 조회에 실패했습니다.")

    return data
