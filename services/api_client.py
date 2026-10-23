import json
import re
from pathlib import Path
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
# 사진 다운로드 및 Windows 로컬 저장
# ==========================================
def download_photo(filename, local_base_path):
    # 사진 파일명이 정해진 형식인지 검증
    match = re.fullmatch(r"[ST]_(\d{8})_\d{6}\.jpg", filename or "")

    if not match:
        raise RuntimeError("사진 파일명 형식이 올바르지 않습니다.")

    # 파일명에서 촬영 날짜 추출
    date = match.group(1)

    # 사진 다운로드 API 주소 생성
    url = "http://{}:{}{}/{}/{}".format(
        SERVER_HOST,
        SERVER_PORT,
        "/photos",
        date,
        filename
    )

    # 사진 다운로드를 위한 GET 요청 객체 생성
    # 사진 데이터는 JSON이 아닌 JPEG 바이너리 형식으로 수신
    request = Request(
        url,
        headers={"Accept": "image/jpeg"},
        method="GET"
    )

    try:
        # 서버에 사진 다운로드 요청을 보내고 응답 데이터 읽기
        with urlopen(request, timeout=SERVER_TIMEOUT) as response:
            photo_data = response.read()
    except HTTPError as error:
        # 서버에서 해당 사진을 찾지 못한 경우
        if error.code == 404:
            raise RuntimeError("서버에서 사진을 찾을 수 없습니다: {}".format(filename))

        # 그 외 HTTP 오류 발생 시 오류 코드 전달
        raise RuntimeError("사진 다운로드 HTTP 오류: {}".format(error.code))
    except (URLError, TimeoutError, OSError) as error:
        # 네트워크 단절, 타임아웃, 시스템 오류 발생 시 예외 처리
        raise RuntimeError("사진 다운로드에 실패했습니다.\n""상세 오류: {}".format(error))

    # 응답 데이터가 비어 있는 경우 파일 저장을 중단
    if not photo_data:
        raise RuntimeError("다운로드한 사진 데이터가 비어 있습니다.")

    # Windows의 로컬 저장 경로 아래에 날짜별 폴더 생성
    date_dir = Path(local_base_path).expanduser() / date
    # 날짜 폴더가 없으면 생성하고, 이미 존재하면 그대로 사용
    date_dir.mkdir(parents=True, exist_ok=True)

    # 원본 사진 파일명을 유지하여 저장
    photo_path = date_dir / filename

    try:
        # JPEG 바이너리 데이터를 파일로 저장
        with open(str(photo_path), "wb") as photo_file:
            photo_file.write(photo_data)
    except OSError as error:
        # 로컬 폴더 접근 권한 또는 디스크 문제 등으로 저장에 실패한 경우
        raise RuntimeError("Windows에 사진을 저장하지 못했습니다.\n""상세 오류: {}".format(photo_path, error))

    # 다운로드 및 저장이 완료된 사진의 전체 경로 반환
    return str(photo_path)