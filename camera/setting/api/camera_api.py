
from common.api.http_client import request_json


def get_cameras():
    """연결된 카메라 목록을 조회합니다.

    Returns:
        list: 연결된 카메라 목록

    Raises:
        RuntimeError: 카메라 목록 조회에 실패한 경우
    """
    status_code, data = request_json("/cameras", method="GET")

    if status_code < 200 or status_code >= 300:
        raise RuntimeError(
            data.get("message", "카메라 목록 조회에 실패했습니다.")
        )

    if not data.get("success", False):
        raise RuntimeError(
            data.get("message", "카메라 목록 조회에 실패했습니다.")
        )

    cameras = data.get("cameras")

    if not isinstance(cameras, list):
        raise RuntimeError("서버의 카메라 목록 응답 형식이 올바르지 않습니다.")

    return cameras


def get_camera_config():
    """저장된 카메라 역할 설정을 조회합니다.

    Returns:
        dict | None: 카메라 역할 설정

    Raises:
        RuntimeError: 카메라 설정 조회 또는 응답 형식이 올바르지 않은 경우
    """
    status_code, data = request_json(
        "/camera-config",
        method="GET"
    )

    if status_code < 200 or status_code >= 300:
        raise RuntimeError(
            data.get("message", "카메라 설정 조회에 실패했습니다.")
        )

    if not data.get("success", False):
        raise RuntimeError(
            data.get("message", "카메라 설정 조회에 실패했습니다.")
        )

    camera_config = data.get("camera_config")

    if camera_config is not None and not isinstance(camera_config, dict):
        raise RuntimeError("서버의 카메라 설정 응답 형식이 올바르지 않습니다.")

    return camera_config


def save_camera_config(side_camera_id=None, top_camera_id=None):
    """카메라 역할 설정을 서버에 저장합니다.

    Args:
        side_camera_id (str, optional): Side 카메라 ID
        top_camera_id (str, optional): Top 카메라 ID

    Returns:
        dict: 저장된 카메라 역할 설정

    Raises:
        RuntimeError: 카메라 역할 설정 저장에 실패한 경우
    """
    payload = {
        "side_camera_id": side_camera_id,
        "top_camera_id": top_camera_id
    }

    status_code, data = request_json(
        "/camera-config",
        method="POST",
        payload=payload
    )

    if status_code < 200 or status_code >= 300 or not data.get("success", False):
        raise RuntimeError(
            data.get("message", "카메라 역할 설정 저장에 실패했습니다.")
        )

    return data.get("camera_config")
