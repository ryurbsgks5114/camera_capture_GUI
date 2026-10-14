# FTP 설정값 검증
def validate_ftp_settings(host, port_text, user, password):
    # 필수 입력값 누락 여부 검증
    if not host or not port_text or not user or not password:
        return False, "FTP 설정 정보를 입력해 주세요.", None

    # Port 번호 유효성 검증
    try:
        port = int(port_text)
        if not 1 <= port <= 65535:
            raise ValueError
    except ValueError:
        return (
            False,
            "FTP Port는 1~65535 사이의 숫자로 입력해 주세요.",
            None
        )

    return True, "", port