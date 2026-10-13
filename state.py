import tkinter as tk
from config import FTP_BASE_DIR
from pathlib import Path

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

        # 촬영 설정 관련 변수
        self.hour_var = tk.StringVar(value="09")
        self.minute_var = tk.StringVar(value="00")
        self.second_var = tk.StringVar(value="00")
        self.interval_var = tk.StringVar(value="10")

        # 저장 경로 설정 관련 변수
        self.local_path = tk.StringVar(value=str(Path.home() / "Downloads"))
        self.ftp_path = tk.StringVar(value=FTP_BASE_DIR)

        # FTP 설정 관련 변수
        self.ftp_host = tk.StringVar(value="")
        self.ftp_port = tk.StringVar(value="")
        self.ftp_user = tk.StringVar(value="")
        self.ftp_password = tk.StringVar(value="")

        # 저장 방식 관련 변수
        self.storage_mode = tk.StringVar(value="both")

        # 촬영 제어 관련 변수
        self.start_time_display = tk.StringVar(value="09:00:00")
        self.interval_display = tk.StringVar(value="10 분")