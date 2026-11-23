import os
import tempfile

from pathlib import Path


def validate_local_path(path_text):
    """로컬 저장 경로의 존재 여부와 쓰기 권한을 검증합니다.

    Args:
        path_text (str): 검증할 로컬 저장 경로

    Returns:
        tuple: 검증 성공 여부와 결과 메시지
    """
    path_text = (path_text or "").strip()

    if not path_text:
        return False, "로컬 저장 경로를 선택해 주세요."

    path = Path(path_text)

    if not path.exists():
        return False, "로컬 저장 경로가 존재하지 않습니다."

    if not path.is_dir():
        return False, "로컬 저장 경로가 폴더가 아닙니다."

    test_file = None

    try:
        file_descriptor, test_file = tempfile.mkstemp(prefix=".camera_manager_test_", dir=str(path))

        os.close(file_descriptor)
        os.remove(test_file)

        return True, "로컬 저장 경로를 확인했습니다."
    except OSError as exc:
        if test_file and os.path.exists(test_file):
            try:
                os.remove(test_file)
            except OSError:
                pass

        return False, "로컬 저장 경로에 쓸 수 없습니다: {}".format(exc)
        