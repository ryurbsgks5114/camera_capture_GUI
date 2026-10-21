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
        raise RuntimeError(data.get("message", "서버 상태 조회에 실패했습니다."))

    return data

# ==========================================
# 촬영 시작 요청 함수
# ==========================================
def start_capture(payload):
    status_code, data = _request_json("/start", method="POST", payload=payload)

    if status_code < 200 or status_code >= 300 or not data.get("success", False):
        raise RuntimeError(data.get("message", "촬영 시작 요청에 실패했습니다."))

    return data

# ==========================================
# 촬영 중지 요청 함수
# ==========================================
def stop_capture():
    status_code, data = _request_json("/stop", method="POST")

    if status_code < 200 or status_code >= 300 or not data.get("success", False):
        raise RuntimeError("촬영 중지 요청에 실패했습니다.")

    return data