from ftplib import FTP, all_errors
import socket

# ==========================================
# FTP 서버 접속, 로그인, 원격 경로 접근을 통한 연결 테스트 함수
# ==========================================
def test_ftp_connection(host, port, user, password, remote_path, timeout=5):
    ftp = FTP()
    connected = False

    try:
        # 서버 접속
        ftp.connect(host, port, timeout=timeout)
        connected = True

        # 로그인
        try:
            ftp.login(user=user, passwd=password)
        except all_errors as err:
            return False, "FTP 로그인 실패: {}".format(err)

        # 원격 저장 경로 접근 확인
        if remote_path:
            try:
                ftp.cwd(remote_path)
            except all_errors as err:
                return False, "원격 경로 접근 실패: {}".format(err)

        return True, "FTP 서버 연결에 성공했습니다."
    except socket.gaierror:
        return False, "FTP 서버 주소를 확인해 주세요."
    except (socket.timeout, TimeoutError):
        return False, "FTP 연결 시간이 초과되었습니다."
    except ConnectionRefusedError:
        return False, "FTP 서버 포트를 확인해 주세요."
    except all_errors as exc:
        return False, "FTP 연결 실패: {}".format(exc)
    finally:
        if connected:
            try:
                ftp.quit()
            except Exception:
                ftp.close()