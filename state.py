import tkinter as tk


class AppState:
    def __init__(self, root):
        self.root = root

        self.server_status = tk.StringVar(value="대기 중")
        self.capture_status = tk.StringVar(value="대기 중")
        self.ftp_status = tk.StringVar(value="대기 중")

        self.hour_var = tk.StringVar(value="09")
        self.minute_var = tk.StringVar(value="00")
        self.second_var = tk.StringVar(value="00")
        self.interval_var = tk.StringVar(value="10")

        self.local_path = tk.StringVar(value="/home/pi/camera_capture/photos")
        self.ftp_path = tk.StringVar(value="/test/camera")

        self.ftp_host = tk.StringVar(value="")
        self.ftp_port = tk.StringVar(value="")
        self.ftp_user = tk.StringVar(value="")
        self.ftp_password = tk.StringVar(value="")

        self.storage_mode = tk.StringVar(value="both")

        self.start_time_display = tk.StringVar(value="09:00:00")
        self.interval_display = tk.StringVar(value="10 분")
