import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from config import SERVER_HOST, SERVER_PORT, SERVER_TIMEOUT

# ==========================================
# 공통 API 요청 및 JSON 응답 처리 함수
# ==========================================
def _request_json(path, method="GET", payload=None):
    # 설정 파일에 정의된 host, port, 경로를 조합하여 요청 URL 생성
    url = "http://{}:{}{}".format(SERVER_HOST, SERVER_PORT, path)
    headers = {"Accept": "application/json"}
    body = None

    # payload(데이터)가 존재할 경우 JSON 형식으로 직렬화하여 요청 헤더와 바디에 설정
    if payload is not None:
        headers["Content-Type"] = "application/json; charset=utf-8"
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    # 앤드포인트로 전송할 Request 객체 생성
    request = Request(url, data=body, headers=headers, method=method)

    try:
        # 서버에 요청을 보내고 응답 처리
        with urlopen(request, timeout=SERVER_TIMEOUT) as response:
            raw = response.read().decode("utf-8")
            data = json.loads(raw) if raw else {}

            return response.status, data
    except HTTPError as error:
        # 서버가 400/500 등의 JSON 오류 응답을 반환한 경우에도
        # GUI에서 서버가 전달한 message를 표시할 수 있도록 본문을 읽는다.
        raw = error.read().decode("utf-8", errors="replace")

        try:
            data = json.loads(raw) if raw else {}
        except ValueError:
            # 응답 본문이 JSON 형식이 아닐 경우 일반 텍스트 메시지로 처리
            data = {"message": raw or "HTTP 오류가 발생했습니다."}
            
        return error.code, data
    except (URLError, TimeoutError, OSError) as error:
        # 네트워크 단절, 타임아웃, 시스템 오류 발생 시 예외 발생
        raise RuntimeError(
            "서버에 연결할 수 없습니다. 서버 주소와 네트워크를 확인해 주세요.\n"
            "상세 오류: {}".format(error)
        )

# ==========================================
# 라즈베리파이 서버 상태 조회 함수
# ==========================================
def get_server_status():
    status_code, data = _request_json("/status", method="GET")

    if status_code != 200:
        raise RuntimeError("서버 상태 조회에 실패했습니다.")

    return data

# ==========================================
# 연결된 카메라 목록 조회 함수
# ==========================================
def get_cameras():
    status_code, data = _request_json("/cameras", method="GET")

    # 서버가 HTTP 오류를 반환한 경우 서버에서 전달한 메시지를 우선 표시
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

# ==========================================
# 저장된 카메라 역할 설정 조회 함수
# ==========================================
def get_camera_config():
    status_code, data = _request_json(
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


# ==========================================
# 카메라 역할 설정 저장 함수
# ==========================================
def save_camera_config(side_camera_id=None, top_camera_id=None):
    payload = {
        "side_camera_id": side_camera_id,
        "top_camera_id": top_camera_id
    }

    status_code, data = _request_json(
        "/camera-config",
        method="POST",
        payload=payload
    )

    if status_code < 200 or status_code >= 300 or not data.get("success", False):
        raise RuntimeError(
            data.get("message", "카메라 역할 설정 저장에 실패했습니다.")
        )

    return data.get("camera_config")

# ==========================================
# 촬영 시작 요청 함수
# ==========================================
def start_capture(payload):
    status_code, data = _request_json("/start", method="POST", payload=payload)

    if status_code < 200 or status_code >= 300 or not data.get("success", False):
        raise RuntimeError("촬영 시작 요청에 실패했습니다.")

    return data

# ==========================================
# 촬영 중지 요청 함수
# ==========================================
def stop_capture():
    status_code, data = _request_json("/stop", method="POST")

    if status_code < 200 or status_code >= 300 or not data.get("success", False):
        raise RuntimeError("촬영 중지 요청에 실패했습니다.")

    return data


# ==========================================
# 카메라 미리보기 시작 요청 함수
# ==========================================
def start_preview():
    status_code, data = _request_json(
        "/preview/start",
        method="POST"
    )

    if (
        status_code < 200
        or status_code >= 300
        or not data.get("success", False)
    ):
        raise RuntimeError(
            data.get("message", "카메라 미리보기 시작에 실패했습니다.")
        )

    return data


# ==========================================
# 카메라 미리보기 중지 요청 함수
# ==========================================
def stop_preview():
    status_code, data = _request_json(
        "/preview/stop",
        method="POST"
    )

    if (
        status_code < 200
        or status_code >= 300
        or not data.get("success", False)
    ):
        raise RuntimeError(
            data.get("message", "카메라 미리보기 중지에 실패했습니다.")
        )

    return data


# ==========================================
# 카메라 최신 미리보기 프레임 조회 함수
# ==========================================
def get_preview_frame(view):
    # Side / Top 이외의 요청은 차단
    if view not in ("side", "top"):
        raise ValueError("잘못된 카메라 구분입니다.")

    url = "http://{}:{}/preview/frame/{}".format(
        SERVER_HOST,
        SERVER_PORT,
        view
    )

    request = Request(
        url,
        headers={"Accept": "image/jpeg"},
        method="GET"
    )

    try:
        with urlopen(request, timeout=SERVER_TIMEOUT) as response:

            # 아직 새로운 프레임이 준비되지 않은 경우
            if response.status == 204:
                return None

            # JPEG 이미지 데이터 반환
            if response.status == 200:
                return response.read()

            raise RuntimeError("미리보기 프레임 조회에 실패했습니다.")

    except HTTPError as error:
        raw = error.read().decode("utf-8", errors="replace")

        try:
            data = json.loads(raw) if raw else {}
        except ValueError:
            data = {}

        raise RuntimeError(
            data.get("message", "미리보기 프레임 조회에 실패했습니다.")
        )

    except (URLError, TimeoutError, OSError) as error:
        raise RuntimeError(
            "서버에 연결할 수 없습니다. 서버 주소와 네트워크를 확인해 주세요.\n"
            "상세 오류: {}".format(error)
        )
