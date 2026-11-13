
import json

from pathlib import Path

from config import FTP_BASE_DIR


PATH_SETTINGS_FILE = Path.home() / ".camera_manager_paths.json"


def load_path_settings():
    """저장된 로컬 및 FTP 경로 설정을 불러옵니다.

    설정 파일이 없거나 읽을 수 없는 경우 기본 경로를 반환합니다.

    Returns:
        dict: 로컬 및 FTP 저장 경로
    """
    default_paths = {
        "local_path": str(Path.home() / "Downloads"),
        "ftp_path": FTP_BASE_DIR
    }

    if not PATH_SETTINGS_FILE.exists():
        return default_paths

    try:
        with PATH_SETTINGS_FILE.open("r", encoding="utf-8") as file:
            saved_paths = json.load(file)

        if not isinstance(saved_paths, dict):
            return default_paths

        local_path = saved_paths.get("local_path")
        ftp_path = saved_paths.get("ftp_path")

        if isinstance(local_path, str) and local_path.strip():
            default_paths["local_path"] = local_path

        if isinstance(ftp_path, str) and ftp_path.strip():
            default_paths["ftp_path"] = ftp_path

        return default_paths
    except (OSError, json.JSONDecodeError):
        return default_paths


def save_path_settings(local_path, ftp_path):
    """로컬 및 FTP 저장 경로를 JSON 파일에 저장합니다.

    Args:
        local_path (str): 로컬 저장 경로
        ftp_path (str): FTP 저장 경로

    Returns:
        bool: 저장 성공 여부
    """
    settings = {
        "local_path": local_path,
        "ftp_path": ftp_path
    }

    try:
        with PATH_SETTINGS_FILE.open("w", encoding="utf-8") as file:
            json.dump(settings, file, ensure_ascii=False, indent=4)

        return True
    except OSError:
        return False
