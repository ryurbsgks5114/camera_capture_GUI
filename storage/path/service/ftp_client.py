
import posixpath
import socket

from ftplib import FTP, all_errors


def _close_ftp(ftp):
    """FTP 연결을 안전하게 종료합니다.

    Args:
        ftp (FTP): 종료할 FTP 연결 객체
    """
    if ftp is None:
        return

    try:
        ftp.quit()
    except Exception:
        try:
            ftp.close()
        except Exception:
            pass


def _connect_ftp(host, port, user, password, timeout=5):
    """FTP 서버에 접속하고 로그인한 객체를 반환합니다.

    Args:
        host (str): FTP 서버 주소
        port (int): FTP 서버 포트
        user (str): FTP 로그인 계정
        password (str): FTP 로그인 비밀번호
        timeout (int): 연결 제한 시간(초)

    Returns:
        FTP: 로그인된 FTP 연결 객체
    """
    ftp = FTP()

    try:
        ftp.connect(host, int(port), timeout=timeout)
        ftp.login(user=user, passwd=password)

        return ftp
    except Exception:
        _close_ftp(ftp)

        raise


def _error_message(exc, action="FTP 연결"):
    """예외 종류에 따라 사용자에게 표시할 메시지를 반환합니다.

    Args:
        exc (Exception): 발생한 예외
        action (str): 실패한 작업 이름

    Returns:
        str: 사용자에게 표시할 오류 메시지
    """
    if isinstance(exc, socket.gaierror):
        return "FTP 서버 주소를 확인해 주세요."

    if isinstance(exc, (socket.timeout, TimeoutError)):
        return "FTP 서버 연결 시간이 초과되었습니다."

    if isinstance(exc, ConnectionRefusedError):
        return "FTP 서버 포트를 확인해 주세요."

    return "{} 실패: {}".format(action, exc)


def test_ftp_connection(host, port, user, password, remote_path, timeout=5):
    """FTP 서버에 접속하고 지정된 원격 경로 접근을 확인합니다.

    Args:
        host (str): FTP 서버 주소
        port (int): FTP 서버 포트
        user (str): FTP 로그인 계정
        password (str): FTP 로그인 비밀번호
        remote_path (str): 연결을 확인할 원격 경로
        timeout (int): 연결 제한 시간(초)

    Returns:
        tuple: 연결 성공 여부와 결과 메시지
    """
    ftp = None

    try:
        ftp = _connect_ftp(host, port, user, password, timeout)

        if remote_path:
            ftp.cwd(remote_path)

        return True, "FTP 서버 연결에 성공했습니다."
    except (socket.gaierror, socket.timeout, TimeoutError, ConnectionRefusedError, OSError, *all_errors) as exc:
        return False, _error_message(exc, "FTP 연결")
    finally:
        _close_ftp(ftp)


def list_ftp_directories(host, port, user, password, remote_path="", timeout=5, fallback_to_home=False):
    """FTP 서버의 지정 경로에서 하위 폴더 목록을 조회합니다.

    지정 경로 조회에 실패하고 기본 경로 재시도가 허용된 경우
    FTP 로그인 기본 경로에서 폴더 목록을 다시 조회합니다.

    Args:
        host (str): FTP 서버 주소
        port (int): FTP 서버 포트
        user (str): FTP 로그인 계정
        password (str): FTP 로그인 비밀번호
        remote_path (str): 조회할 원격 경로
        timeout (int): 연결 제한 시간(초)
        fallback_to_home (bool): 실패 시 기본 경로 재시도 여부

    Returns:
        tuple: 성공 여부, 결과 메시지, 현재 경로, 하위 폴더 목록
    """
    ftp = None
    result = None

    try:
        ftp = _connect_ftp(host, port, user, password, timeout)

        if remote_path:
            ftp.cwd(remote_path)

        current_path = ftp.pwd()
        directories = []
        listing_error = None

        try:
            for name, facts in ftp.mlsd():
                if name not in (".", "..") and facts.get("type", "").lower() == "dir":
                    directories.append(name)
        except all_errors + (AttributeError, NotImplementedError):
            directories = []

            try:
                entries = ftp.nlst()
            except all_errors as exc:
                listing_error = _error_message(exc, "FTP 폴더 목록 조회")
            else:
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
                        try:
                            ftp.cwd(current_path)
                        except all_errors:
                            pass

        if listing_error:
            result = (False, listing_error, current_path, [])
        else:
            directories = sorted(set(directories), key=str.lower)
            result = (True, "FTP 폴더 목록을 불러왔습니다.", current_path, directories)
    except (socket.gaierror, socket.timeout, TimeoutError, ConnectionRefusedError, OSError, *all_errors) as exc:
        result = (False, _error_message(exc, "FTP 폴더 조회"), "", [])
    finally:
        _close_ftp(ftp)

    if result[0] or not fallback_to_home or not remote_path:
        return result

    fallback_result = list_ftp_directories(host=host, port=port, user=user, password=password, remote_path="", timeout=timeout)

    if not fallback_result[0]:
        return result

    return (True, "저장된 경로에 접근할 수 없어 FTP 기본 경로를 표시합니다.", fallback_result[2], fallback_result[3])
