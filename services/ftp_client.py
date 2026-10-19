from ftplib import FTP, all_errors
import posixpath
import socket

# ==========================================
# FTP 서버에 접속하고 로그인한 FTP 객체를 반환하는 함수
# ==========================================
def _connect_ftp(host, port, user, password, timeout=5):
    ftp = FTP()
    ftp.connect(host, int(port), timeout=timeout)
    ftp.login(user=user, passwd=password)

    return ftp

# ==========================================
# 예외 종류에 따라 에러 메시지를 반환하는 함수
# ==========================================
def _error_message(exc, action="FTP 연결"):
    if isinstance(exc, socket.gaierror):
        return "FTP 서버 주소를 확인해 주세요."
    if isinstance(exc, (socket.timeout, TimeoutError)):
        return "FTP 서버 연결 시간이 초과되었습니다."
    if isinstance(exc, ConnectionRefusedError):
        return "FTP 서버 포트를 확인해 주세요."
    return "{} 실패: {}".format(action, exc)

# ==========================================
# FTP 서버 접속, 로그인, 원격 경로 접근을 통한 연결 테스트 함수
# ==========================================
def test_ftp_connection(host, port, user, password, remote_path, timeout=5):
    ftp = FTP()

    try:
        # FTP 서버 연결 및 로그인 수행
        ftp = _connect_ftp(host, port, user, password, timeout)

        # 원격 경로가 지정되어 있는 경우 해당 경로로 이동
        if remote_path:
            ftp.cwd(remote_path)
        
        return True, "FTP 서버 연결에 성공했습니다."
    except (socket.gaierror, socket.timeout, TimeoutError,
            ConnectionRefusedError, OSError, *all_errors) as exc:
        return False, _error_message(exc, "FTP 연결")
    finally:
        # 연결 종료 시 안전하게 리소스 해제
        if ftp is not None:
            try:
                ftp.quit()
            except Exception:
                ftp.close()

# ==========================================
# FTP 서버의 지정 경로에서 하위 폴더 목록을 조회하는 함수
# ==========================================
def list_ftp_directories(host, port, user, password, remote_path="", timeout=5):
    ftp = None

    try:
        # FTP 서버 연결 및 로그인 수행
        ftp = _connect_ftp(host, port, user, password, timeout)

        # 원격 경로가 지정되어 있는 경우 해당 경로로 이동
        if remote_path:
            ftp.cwd(remote_path)

        current_path = ftp.pwd()
        directories = []

        # 표준 방식인 MLSD를 우선 사용하여 디렉토리 목록 조회
        try:
            for name, facts in ftp.mlsd():
                # 상위/현재 디렉토리 기호 제외 및 폴더 타입인 항목만 추출
                if name not in (".", "..") and facts.get("type", "").lower() == "dir":
                    directories.append(name)
        except all_errors + (AttributeError, NotImplementedError):
            directories = []

            # MLSD를 지원하지 않는 구형 서버인 경우 NLST를 이용해 이름 목록만 가져옴
            try:
                entries = ftp.nlst()
            except all_errors as exc:
                return False, _error_message(exc, "FTP 폴더 목록 조회"), current_path, []

            # 가져온 엔트리들을 순회하며 실제 디렉토리인지 CWD 명령으로 판별
            for entry in entries:
                name = posixpath.basename(entry.rstrip("/"))

                if not name or name in (".", ".."):
                    continue
                try:
                    ftp.cwd(entry)
                    directories.append(name)
                except all_errors:
                    pass
                finally:
                    # 확인 작업 후 항상 원래의 기준 경로로 복귀
                    try:
                        ftp.cwd(current_path)
                    except all_errors:
                        pass

        # 중복 제거 및 알파벳 대소문자 구분 없는 정렬 수행
        directories = sorted(set(directories), key=str.lower)

        return True, "FTP 폴더 목록을 불러왔습니다.", current_path, directories
    except (socket.gaierror, socket.timeout, TimeoutError, ConnectionRefusedError, OSError, *all_errors) as exc:
        return False, _error_message(exc, "FTP 폴더 조회"), "", []
    finally:
        # 연결 종료 시 안전하게 리소스 해제
        if ftp is not None:
            try:
                ftp.quit()
            except Exception:
                ftp.close()