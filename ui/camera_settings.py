import threading
import tkinter as tk
from config import WHITE, TEXT, SUBTEXT, BLUE, GREEN, RED, GRAY, BLUE_LIGHT
from services.api_client import get_cameras
from ui.common import create_panel


# ==========================================
# 연결된 카메라 목록 UI 및 조회 기능
# ==========================================
def build(parent, app):
    panel = create_panel(
        parent,
        "카메라 연결 상태",
        "↻  목록 새로고침",
        lambda: refresh_camera_list()
    )
    panel.pack(fill="x", pady=5)

    body = tk.Frame(panel, bg=WHITE)
    body.pack(fill="x", padx=20, pady=10)

    status_label = tk.Label(
        body,
        text="카메라 목록을 확인하고 있습니다...",
        bg=WHITE,
        fg=SUBTEXT,
        anchor="w",
        font=("Malgun Gothic", 9)
    )
    status_label.pack(fill="x", pady=(0, 5))

    camera_list_frame = tk.Frame(body, bg=WHITE)
    camera_list_frame.pack(fill="x")

    refresh_in_progress = False

    # ==========================================
    # 조회 결과에 맞춰 카메라 목록 다시 표시
    # ==========================================
    def render_cameras(cameras):
        for widget in camera_list_frame.winfo_children():
            widget.destroy()

        if not cameras:
            tk.Label(
                camera_list_frame,
                text="연결된 카메라가 없습니다.",
                bg=WHITE,
                fg=RED,
                anchor="w",
                font=("Malgun Gothic", 9)
            ).pack(fill="x", pady=4)
            return

        for index, camera in enumerate(cameras, start=1):
            if not isinstance(camera, dict):
                continue

            available = camera.get("available") is True
            camera_name = str(camera.get("name") or "이름 없는 카메라")
            status_text = "촬영 가능" if available else "촬영 장치 확인 필요"
            status_color = GREEN if available else RED

            row = tk.Frame(
                camera_list_frame,
                bg=BLUE_LIGHT if available else WHITE,
                highlightbackground="#D8E2EF",
                highlightthickness=1
            )
            row.pack(fill="x", pady=3)

            tk.Label(
                row,
                text="카메라 {}  |  {}".format(index, camera_name),
                bg=row.cget("bg"),
                fg=TEXT,
                anchor="w",
                font=("Malgun Gothic", 9, "bold"),
                padx=9,
                pady=7
            ).pack(side="left", fill="x", expand=True)

            tk.Label(
                row,
                text=status_text,
                bg=row.cget("bg"),
                fg=status_color,
                font=("Malgun Gothic", 8, "bold"),
                padx=9
            ).pack(side="right")

    # ==========================================
    # 서버 카메라 목록 조회 결과를 UI에 반영
    # ==========================================
    def finish_request(cameras, error_message):
        nonlocal refresh_in_progress
        refresh_in_progress = False

        if not panel.winfo_exists():
            return

        if error_message is not None:
            status_label.configure(
                text="카메라 목록을 불러오지 못했습니다. {}".format(error_message),
                fg=RED
            )
            return

        available_count = sum(
            1 for camera in cameras
            if isinstance(camera, dict) and camera.get("available") is True
        )

        status_label.configure(
            text="검색된 카메라: {}대  |  촬영 가능: {}대".format(
                len(cameras), available_count
            ),
            fg=GREEN if available_count else GRAY
        )
        render_cameras(cameras)

    # ==========================================
    # 백그라운드 스레드에서 서버 카메라 목록 조회
    # ==========================================
    def refresh_camera_list():
        nonlocal refresh_in_progress

        if refresh_in_progress:
            return

        refresh_in_progress = True
        status_label.configure(
            text="서버에서 카메라 목록을 확인하고 있습니다...",
            fg=BLUE
        )

        def worker():
            try:
                cameras = get_cameras()
                error_message = None
            except Exception as error:
                cameras = []
                error_message = str(error)

            try:
                app.root.after(
                    0,
                    lambda: finish_request(cameras, error_message)
                )
            except tk.TclError:
                # 조회 중 GUI가 종료된 경우 UI 갱신 생략
                pass

        threading.Thread(
            target=worker,
            name="CameraListRequestThread",
            daemon=True
        ).start()

    # GUI가 만들어진 뒤 최초 카메라 목록 자동 조회
    app.root.after(100, refresh_camera_list)

    return panel
