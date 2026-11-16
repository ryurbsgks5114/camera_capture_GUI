
def validate_capture_settings(hour_text, minute_text, second_text, interval_text,):
    """촬영 시작 시간과 촬영 간격 입력값을 검증합니다.

    Args:
        hour_text (str): 촬영 시작 시간의 시 입력값
        minute_text (str): 촬영 시작 시간의 분 입력값
        second_text (str): 촬영 시작 시간의 초 입력값
        interval_text (str): 촬영 간격 입력값

    Returns:
        tuple: 검증 성공 여부와 결과 메시지
    """
    time_fields = [
        ("시", hour_text, 0, 23),
        ("분", minute_text, 0, 59),
        ("초", second_text, 0, 59)
    ]

    for label, value, min_value, max_value in time_fields:
        value = value.strip()

        if not value.isascii() or not value.isdigit():
            return False, f"촬영 시작 시간의 {label}을(를) 숫자로 입력해 주세요."

        number = int(value)

        if not min_value <= number <= max_value:
            return False, (
                f"촬영 시작 시간의 {label}은(는) "
                f"{min_value}~{max_value} 사이로 입력해 주세요."
            )

    interval_text = interval_text.strip()

    if not interval_text.isascii() or not interval_text.isdigit():
        return False, "촬영 간격은 양의 정수로 입력해 주세요."

    interval = int(interval_text)

    if interval <= 0:
        return False, "촬영 간격은 1 이상의 정수로 입력해 주세요."

    return True, ""
