import json
import tkinter as tk
from config import (
    FTP_BASE_DIR,
    DEFAULT_STORAGE_MODE,
    DEFAULT_INTERVAL_MINUTES,
    DEFAULT_START_HOUR,
    DEFAULT_START_MINUTE,
    DEFAULT_START_SECOND
)
from pathlib import Path

# 저장 경로 설정 파일
PATH_SETTINGS_FILE = Path.home() / ".camera_manager_paths.json"

# ==========================================
# 저장된 로컬 및 FTP 경로 불러오기
# ==========================================
def load_path_settings():
    # 기존 기본 경로를 기본값으로 사용
    default_paths = {
        "local_path": str(Path.home() / "Downloads"),
        "ftp_path": FTP_BASE_DIR
    }

    # 설정 파일이 없으면 기본 경로 반환
    if not PATH_SETTINGS_FILE.exists():
        return default_paths

    try:
        # JSON 파일에서 저장 경로 읽기
        with PATH_SETTINGS_FILE.open("r", encoding="utf-8") as file:
            saved_paths = json.load(file)

        # 저장 데이터가 딕셔너리인지 확인
        if not isinstance(saved_paths, dict):
            return default_paths

        # 저장된 경로가 문자열인 경우에만 적용
        local_path = saved_paths.get("local_path")
        ftp_path = saved_paths.get("ftp_path")

        if isinstance(local_path, str) and local_path.strip():
            default_paths["local_path"] = local_path

        if isinstance(ftp_path, str) and ftp_path.strip():
            default_paths["ftp_path"] = ftp_path

        return default_paths
    except (OSError, json.JSONDecodeError):
        # 파일이 없거나 내용이 잘못된 경우 기본 경로 사용
        return default_paths

# ==========================================
# 애플리케이션의 전체 상태를 관리하는 클래스
# ==========================================
class AppState:
    # 상태 변수 초기화
    def __init__(self, root):
        self.root = root

        # 시스템 상태 관련 변수
        self.server_status = tk.StringVar(value="대기 중")
        self.capture_status = tk.StringVar(value="대기 중")
        self.ftp_status = tk.StringVar(value="대기 중")
        self.websocket_status = tk.StringVar(value="연결 중")

        # 촬영 설정 관련 변수
        self.hour_var = tk.StringVar(value=DEFAULT_START_HOUR)
        self.minute_var = tk.StringVar(value=DEFAULT_START_MINUTE)
        self.second_var = tk.StringVar(value=DEFAULT_START_SECOND)
        self.interval_var = tk.StringVar(value=DEFAULT_INTERVAL_MINUTES)

        # 저장된 로컬 및 FTP 경로 불러오기
        path_settings = load_path_settings()

        # 저장 경로 설정 관련 변수
        self.local_path = tk.StringVar(value=path_settings["local_path"])
        self.ftp_path = tk.StringVar(value=path_settings["ftp_path"])

        # FTP 설정 관련 변수
        self.ftp_host = tk.StringVar(value="")
        self.ftp_port = tk.StringVar(value="")
        self.ftp_user = tk.StringVar(value="")
        self.ftp_password = tk.StringVar(value="")

        # 저장 방식 관련 변수
        self.storage_mode = tk.StringVar(value=DEFAULT_STORAGE_MODE)

        # 촬영 제어 관련 변수
        self.start_time_display = tk.StringVar(
            value="{:02d}:{:02d}:{:02d}".format(
                int(DEFAULT_START_HOUR),
                int(DEFAULT_START_MINUTE),
                int(DEFAULT_START_SECOND)
            )
        )
        self.interval_display = tk.StringVar(value="{} 분".format(DEFAULT_INTERVAL_MINUTES))

    # ==========================================
    # 저장 경로 설정을 JSON 파일에 저장하는 함수
    # ==========================================
    def save_path_settings(self):
        settings = {
            "local_path": self.local_path.get(),
            "ftp_path": self.ftp_path.get()
        }

        try:
            with PATH_SETTINGS_FILE.open("w", encoding="utf-8") as file:
                json.dump(
                    settings,
                    file,
                    ensure_ascii=False,
                    indent=4
                )
                
            return True
        except OSError:
            return False