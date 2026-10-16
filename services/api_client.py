import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from config import SERVER_HOST, SERVER_PORT, SERVER_TIMEOUT

# API 요청하고 JSON 응답을 반환하는 함수
def _request_json(path, method="GET", payload=None):
    url = "http://{}:{}{}".format(SERVER_HOST, SERVER_PORT, path)
    headers = {"Accept": "application/json"}
    body = None

    if payload is not None:
        headers["Content-Type"] = "application/json; charset=utf-8"
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    request = Request(url, data=body, headers=headers, method=method)

    try:
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
            data = {"message": raw or "HTTP 오류가 발생했습니다."}
        return error.code, data
    except (URLError, TimeoutError, OSError) as error:
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
        raise RuntimeError(data.get("message", "서버 상태 조회에 실패했습니다."))

    return data

# 촬영 시작 요청 함수
def start_capture(payload):
    status_code, data = _request_json("/start", method="POST", payload=payload)

    if status_code < 200 or status_code >= 300 or not data.get("success", False):
        raise RuntimeError(data.get("message", "촬영 시작 요청에 실패했습니다."))

    return data