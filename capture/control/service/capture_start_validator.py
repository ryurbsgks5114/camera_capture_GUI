
from capture.setting.service.capture_settings_validator import validate_capture_settings
from storage.path.service.path_validator import validate_local_path


def validate_capture_start_settings(hour_text, minute_text, second_text, interval_text, storage_mode, local_path, ftp_path,):
    """촬영 시작에 필요한 설정값과 저장 경로를 검증합니다.

    Args:
        hour_text (str): 촬영 시작 시간의 시 입력값
        minute_text (str): 촬영 시작 시간의 분 입력값
        second_text (str): 촬영 시작 시간의 초 입력값
        interval_text (str): 촬영 간격 입력값
        storage_mode (str): 저장 방식 (ftp, local, both)
        local_path (str): 로컬 저장 경로
        ftp_path (str): FTP 저장 경로

    Returns:
        tuple: 검증 성공 여부와 결과 메시지
    """
    valid, message = validate_capture_settings(
        hour_text=hour_text,
        minute_text=minute_text,
        second_text=second_text,
        interval_text=interval_text,
    )

    if not valid:
        return False, message

    if storage_mode in ("local", "both"):
        valid, message = validate_local_path(local_path)

        if not valid:
            return False, message

    if storage_mode in ("ftp", "both"):
        if not (ftp_path or "").strip():
            return False, "FTP 저장 경로를 선택해 주세요."

    return True, ""
