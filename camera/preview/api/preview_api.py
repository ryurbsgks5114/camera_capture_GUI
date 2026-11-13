
from common.api.http_client import request_json, request_bytes


def start_preview():
    """카메라 미리보기를 시작하도록 서버에 요청합니다.

    Returns:
        dict: 서버 응답 데이터

    Raises:
        RuntimeError: 미리보기 시작에 실패한 경우
    """
    status_code, data = request_json("/preview/start", method="POST")

    if (status_code < 200 or status_code >= 300 or not data.get("success", False)):
        raise RuntimeError(data.get("message", "카메라 미리보기 시작에 실패했습니다."))

    return data


def stop_preview():
    """카메라 미리보기를 중지하도록 서버에 요청합니다.

    Returns:
        dict: 서버 응답 데이터

    Raises:
        RuntimeError: 미리보기 중지에 실패한 경우
    """
    status_code, data = request_json("/preview/stop", method="POST")

    if (status_code < 200 or status_code >= 300 or not data.get("success", False)):
        raise RuntimeError(data.get("message", "카메라 미리보기 중지에 실패했습니다."))

    return data


def get_preview_frame(view):
    """지정된 카메라의 최신 미리보기 프레임을 조회합니다.

    Args:
        view (str): 카메라 구분값 (side 또는 top)

    Returns:
        bytes | None: JPEG 이미지 데이터 또는 프레임이 없는 경우 None

    Raises:
        ValueError: 잘못된 카메라 구분값인 경우
        RuntimeError: 미리보기 프레임 조회에 실패한 경우
    """
    if view not in ("side", "top"):
        raise ValueError("잘못된 카메라 구분입니다.")

    return request_bytes("/preview/frame/{}".format(view), error_message="미리보기 프레임 조회에 실패했습니다.")
