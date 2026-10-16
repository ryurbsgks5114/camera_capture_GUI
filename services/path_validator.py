from pathlib import Path
import os
import tempfile

# ==========================================
# 로컬 저장 경로 유효성 및 쓰기 권한 검증 함수
# ==========================================
def validate_local_path(path_text):
    # 입력된 경로 문자열이 비어있는 경우 대비
    path_text = (path_text or "").strip()

    # 경로가 비어있는 경우 오류 반환
    if not path_text:
        return False, "로컬 저장 경로를 선택해 주세요."

    path = Path(path_text)

    # 경로가 실제 시스템상에 존재하는지 확인
    if not path.exists():
        return False, "로컬 저장 경로가 존재하지 않습니다."

    # 경로가 폴더인지 확인
    if not path.is_dir():
        return False, "로컬 저장 경로가 폴더가 아닙니다."

    test_file = None

    try:
        # 해당 폴더에 쓰기 권한이 존재하는지 테스트하기 위해 고유한 임시 파일 생성
        fd, test_file = tempfile.mkstemp(
            prefix=".camera_manager_test_",
            dir=str(path)
        )

        os.close(fd)

        # 생성한 임시 파일 삭제
        os.remove(test_file)

        return True, "로컬 저장 경로를 확인했습니다."
    except OSError as exc:
        # 검사 중 실패하면 생성한 임시 파일만 정리
        if test_file and os.path.exists(test_file):
            try:
                os.remove(test_file)
            except OSError:
                pass

        return False, "로컬 저장 경로에 쓸 수 없습니다: {}".format(exc)