# ==========================================
# 사용자 입력 촬영 설정값(시, 분, 초, 촬영 간격) 검증 함수
# ==========================================
def validate_capture_settings(hour_text, minute_text, second_text, interval_text):
    # 촬영 시작 시간의 시·분·초 입력값 검증 항목 정의
    time_fields = [
        ("시", hour_text, 0, 23),
        ("분", minute_text, 0, 59),
        ("초", second_text, 0, 59)
    ]

    # 각 필드별 공백 제거 및 유효 범위 검사 수행
    for label, value, min_value, max_value in time_fields:
        value = value.strip()

        # 입력값이 비어있거나 ASCII 숫자가 아닌 경우 오류 반환
        if not value.isascii() or not value.isdigit():
            return False, f"촬영 시작 시간의 {label}을(를) 숫자로 입력해 주세요."

        number = int(value)

        # 각 항목의 허용 범위 확인
        if not min_value <= number <= max_value:
            return False, (
                f"촬영 시작 시간의 {label}은(는) "
                f"{min_value}~{max_value} 사이로 입력해 주세요."
            )

    # 촬영 간격 검증
    interval_text = interval_text.strip()

    # 입력값이 비어있거나 ASCII 숫자가 아닌 경우 오류 반환
    if not interval_text.isascii() or not interval_text.isdigit():
        return False, "촬영 간격은 양의 정수로 입력해 주세요."

    interval = int(interval_text)

    # 촬영 간격이 0 이하인지 확인
    if interval <= 0:
        return False, "촬영 간격은 1 이상의 정수로 입력해 주세요."

    return True, ""