
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from config import SERVER_HOST, SERVER_PORT, SERVER_TIMEOUT


def _build_url(path):
    """서버 주소와 요청 경로를 조합하여 URL을 생성합니다.

    Args:
        path (str): 서버 API 요청 경로

    Returns:
        str: 완성된 요청 URL
    """
    return "http://{}:{}{}".format(
        SERVER_HOST,
        SERVER_PORT,
        path
    )


def _create_request(path, method="GET", payload=None, accept="application/json"):
    """HTTP 요청 객체를 생성합니다.

    Args:
        path (str): 서버 API 요청 경로
        method (str, optional): HTTP 요청 방식
        payload (dict, optional): 서버로 전달할 데이터
        accept (str, optional): 요청 응답 데이터 형식

    Returns:
        Request: 생성된 HTTP 요청 객체
    """
    headers = {"Accept": accept}
    body = None

    if payload is not None:
        headers["Content-Type"] = "application/json; charset=utf-8"
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    return Request(
        _build_url(path),
        data=body,
        headers=headers,
        method=method
    )


def _create_connection_error(error):
    """서버 연결 오류를 RuntimeError로 변환합니다.

    Args:
        error (Exception): 발생한 네트워크 오류

    Returns:
        RuntimeError: 사용자에게 전달할 연결 오류
    """
    return RuntimeError(
        "서버에 연결할 수 없습니다. 서버 주소와 네트워크를 확인해 주세요.\n"
        "상세 오류: {}".format(error)
    )


def request_json(path, method="GET", payload=None):
    """JSON 형식의 HTTP 요청을 전송하고 응답을 반환합니다.

    Args:
        path (str): 서버 API 요청 경로
        method (str, optional): HTTP 요청 방식
        payload (dict, optional): 서버로 전달할 데이터

    Returns:
        tuple: HTTP 상태 코드와 JSON 응답 데이터

    Raises:
        RuntimeError: 서버 연결에 실패한 경우
    """
    request = _create_request(
        path,
        method=method,
        payload=payload
    )

    try:
        with urlopen(request, timeout=SERVER_TIMEOUT) as response:
            raw = response.read().decode("utf-8")
            data = json.loads(raw) if raw else {}

            return response.status, data

    except HTTPError as error:
        raw = error.read().decode("utf-8", errors="replace")

        try:
            data = json.loads(raw) if raw else {}
        except ValueError:
            data = {"message": raw or "HTTP 오류가 발생했습니다."}

        return error.code, data

    except (URLError, TimeoutError, OSError) as error:
        raise _create_connection_error(error)


def request_bytes(
    path,
    accept="image/jpeg",
    error_message="바이너리 데이터 조회에 실패했습니다."
):
    """바이너리 형식의 HTTP 응답을 반환합니다.

    Args:
        path (str): 서버 API 요청 경로
        accept (str, optional): 요청 응답 데이터 형식
        error_message (str, optional): 요청 실패 시 표시할 오류 메시지

    Returns:
        bytes | None: 응답 데이터 또는 새 프레임이 없는 경우 None

    Raises:
        RuntimeError: 서버 요청 또는 응답 처리에 실패한 경우
    """
    request = _create_request(
        path,
        accept=accept
    )

    try:
        with urlopen(request, timeout=SERVER_TIMEOUT) as response:
            if response.status == 204:
                return None

            if response.status == 200:
                return response.read()

            raise RuntimeError(error_message)

    except HTTPError as error:
        raw = error.read().decode("utf-8", errors="replace")

        try:
            data = json.loads(raw) if raw else {}
        except ValueError:
            data = {}

        raise RuntimeError(
            data.get("message", error_message)
        )

    except (URLError, TimeoutError, OSError) as error:
        raise _create_connection_error(error)
