
from capture.setting.service.capture_settings_validator import validate_capture_settings
from storage.path.service.path_validator import validate_local_path


# ==========================================
# 촬영 시작 전에 GUI에서 수행할 전체 입력값 검증
# ==========================================
def validate_capture_start_settings(
    hour_text,
    minute_text,
    second_text,
    interval_text,
    storage_mode,
    local_path,
    ftp_path,
):
    # 촬영 시간 및 간격 검증
    valid, message = validate_capture_settings(
        hour_text=hour_text,
        minute_text=minute_text,
        second_text=second_text,
        interval_text=interval_text,
    )

    if not valid:
        return False, message

    # 로컬 저장 경로 검증
    if storage_mode in ("local", "both"):
        valid, message = validate_local_path(local_path)

        if not valid:
            return False, message

    # FTP 저장 경로 선택 여부 확인
    if storage_mode in ("ftp", "both"):
        if not (ftp_path or "").strip():
            return False, "FTP 저장 경로를 선택해 주세요."

    return True, ""
