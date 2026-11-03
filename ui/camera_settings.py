import threading
import tkinter as tk

from config import (
    WHITE,
    TEXT,
    SUBTEXT,
    BLUE,
    GREEN,
    RED,
    GRAY,
    BLUE_LIGHT
)

from services.api_client import (
    get_cameras,
    get_camera_config,
    save_camera_config
)

from ui.common import create_panel


# ==========================================
# 연결된 카메라 목록 UI 및 역할 설정 기능
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

    # 현재 저장된 역할 설정
    camera_config = {
        "side_camera_id": None,
        "top_camera_id": None
    }

    # 서버 요청 중복 실행 방지
    request_in_progress = False

    # ==========================================
    # 역할 이름 변환
    # ==========================================
    def get_role_text(role):
        if role == "side":
            return "사이드 카메라"
        elif role == "top":
            return "탑 카메라"

        return "역할 미지정"

    # ==========================================
    # 버튼 생성
    # ==========================================
    def create_action_button(parent, text, command, enabled=True):
        return tk.Button(
            parent,
            text=text,
            command=command,
            state=tk.NORMAL if enabled else tk.DISABLED,
            bg=WHITE,
            fg=BLUE if enabled else GRAY,
            activebackground=BLUE_LIGHT,
            activeforeground=BLUE,
            relief="solid",
            bd=1,
            highlightthickness=0,
            font=("Malgun Gothic", 8, "bold"),
            padx=8,
            pady=4,
            cursor="hand2"
        )

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

            camera_id = camera.get("location_id")
            available = camera.get("available") is True

            camera_name = str(
                camera.get("name") or "이름 없는 카메라"
            )

            role = camera.get("role")

            status_text = (
                "촬영 가능"
                if available
                else "촬영 장치 확인 필요"
            )

            status_color = GREEN if available else RED

            # 카메라 한 대를 표시하는 영역
            row = tk.Frame(
                camera_list_frame,
                bg=BLUE_LIGHT if available else WHITE,
                highlightbackground="#D8E2EF",
                highlightthickness=1
            )
            row.pack(fill="x", pady=3)

            # ==================================
            # 카메라 이름 및 연결 상태
            # ==================================
            info_frame = tk.Frame(
                row,
                bg=row.cget("bg")
            )
            info_frame.pack(
                fill="x",
                padx=9,
                pady=(7, 3)
            )

            tk.Label(
                info_frame,
                text="카메라 {}  |  {}".format(index, camera_name),
                bg=row.cget("bg"),
                fg=TEXT,
                anchor="w",
                font=("Malgun Gothic", 9, "bold")
            ).pack(side="left", fill="x", expand=True)

            tk.Label(
                info_frame,
                text=status_text,
                bg=row.cget("bg"),
                fg=status_color,
                font=("Malgun Gothic", 8, "bold")
            ).pack(side="right")

            # ==================================
            # 현재 역할 표시
            # ==================================
            role_frame = tk.Frame(
                row,
                bg=row.cget("bg")
            )
            role_frame.pack(
                fill="x",
                padx=9,
                pady=(2, 7)
            )

            role_color = (
                BLUE
                if role in ("side", "top")
                else GRAY
            )

            tk.Label(
                role_frame,
                text="현재 역할: {}".format(get_role_text(role)),
                bg=row.cget("bg"),
                fg=role_color,
                font=("Malgun Gothic", 8, "bold")
            ).pack(side="left", fill="x", expand=True)

            # ==================================
            # Side / Top / 역할 해제 버튼
            # ==================================
            button_frame = tk.Frame(
                role_frame,
                bg=row.cget("bg")
            )
            button_frame.pack(side="right")

            # 현재 Side로 지정된 카메라는 Side 버튼 비활성화
            create_action_button(
                button_frame,
                "Side 지정",
                lambda cid=camera_id: change_camera_role(
                    cid,
                    "side"
                ),
                enabled=available and role != "side"
            ).pack(side="left", padx=2)

            # 현재 Top으로 지정된 카메라는 Top 버튼 비활성화
            create_action_button(
                button_frame,
                "Top 지정",
                lambda cid=camera_id: change_camera_role(
                    cid,
                    "top"
                ),
                enabled=available and role != "top"
            ).pack(side="left", padx=2)

            # 역할이 지정된 카메라만 해제 가능
            create_action_button(
                button_frame,
                "해제",
                lambda cid=camera_id: clear_camera_role(cid),
                enabled=role in ("side", "top")
            ).pack(side="left", padx=2)

    # ==========================================
    # 서버 요청 완료 후 UI 갱신
    # ==========================================
    def finish_request(cameras, config, error_message, notice=None):
        nonlocal request_in_progress
        nonlocal camera_config

        request_in_progress = False

        if not panel.winfo_exists():
            return

        if error_message is not None:
            status_label.configure(
                text="카메라 설정 처리에 실패했습니다. {}".format(
                    error_message
                ),
                fg=RED
            )

            app.notify(error_message, RED)
            return

        camera_config = config or {
            "side_camera_id": None,
            "top_camera_id": None
        }

        available_count = sum(
            1
            for camera in cameras
            if isinstance(camera, dict)
            and camera.get("available") is True
        )

        status_label.configure(
            text="검색된 카메라: {}대  |  촬영 가능: {}대".format(
                len(cameras),
                available_count
            ),
            fg=GREEN if available_count else GRAY
        )

        render_cameras(cameras)

        if notice:
            app.notify(notice, GREEN)

    # ==========================================
    # 서버에서 카메라 목록 및 역할 설정 조회
    # ==========================================
    def refresh_camera_list():
        nonlocal request_in_progress

        if request_in_progress:
            return

        request_in_progress = True

        status_label.configure(
            text="서버에서 카메라 목록을 확인하고 있습니다...",
            fg=BLUE
        )

        def worker():
            try:
                cameras = get_cameras()
                config = get_camera_config()

                error_message = None

            except Exception as error:
                cameras = []
                config = None
                error_message = str(error)

            try:
                app.root.after(
                    0,
                    lambda: finish_request(
                        cameras,
                        config,
                        error_message
                    )
                )

            except tk.TclError:
                pass

        threading.Thread(
            target=worker,
            name="CameraListRequestThread",
            daemon=True
        ).start()

    # ==========================================
    # 카메라 역할 변경
    # ==========================================
    def change_camera_role(camera_id, role):
        if not camera_id:
            return

        if role not in ("side", "top"):
            return

        side_camera_id = camera_config.get("side_camera_id")
        top_camera_id = camera_config.get("top_camera_id")

        # 동일 카메라를 두 역할에 지정하지 못하도록 방지
        if role == "side":
            if top_camera_id == camera_id:
                app.notify(
                    "이미 탑 카메라로 지정되어 있습니다. "
                    "먼저 탑 역할을 해제해 주세요.",
                    RED
                )
                return

            side_camera_id = camera_id

        elif role == "top":
            if side_camera_id == camera_id:
                app.notify(
                    "이미 사이드 카메라로 지정되어 있습니다. "
                    "먼저 사이드 역할을 해제해 주세요.",
                    RED
                )
                return

            top_camera_id = camera_id

        update_camera_config(
            side_camera_id,
            top_camera_id,
            "카메라 역할을 변경했습니다."
        )

    # ==========================================
    # 카메라 역할 해제
    # ==========================================
    def clear_camera_role(camera_id):
        side_camera_id = camera_config.get("side_camera_id")
        top_camera_id = camera_config.get("top_camera_id")

        if side_camera_id == camera_id:
            side_camera_id = None

        if top_camera_id == camera_id:
            top_camera_id = None

        update_camera_config(
            side_camera_id,
            top_camera_id,
            "카메라 역할을 해제했습니다."
        )

    # ==========================================
    # 변경된 카메라 역할을 서버에 저장
    # ==========================================
    def update_camera_config(
        side_camera_id,
        top_camera_id,
        notice
    ):
        nonlocal request_in_progress

        if request_in_progress:
            return

        request_in_progress = True

        status_label.configure(
            text="카메라 역할 설정을 저장하고 있습니다...",
            fg=BLUE
        )

        def worker():
            try:
                # 서버에 변경된 역할 설정 저장
                save_camera_config(
                    side_camera_id,
                    top_camera_id
                )

                # 저장된 설정을 적용한 최신 카메라 목록 조회
                cameras = get_cameras()
                config = get_camera_config()

                error_message = None

            except Exception as error:
                cameras = []
                config = None
                error_message = str(error)

            try:
                app.root.after(
                    0,
                    lambda: finish_request(
                        cameras,
                        config,
                        error_message,
                        notice if error_message is None else None
                    )
                )

            except tk.TclError:
                pass

        threading.Thread(
            target=worker,
            name="CameraConfigRequestThread",
            daemon=True
        ).start()

    # GUI가 만들어진 뒤 최초 카메라 목록 자동 조회
    app.root.after(100, refresh_camera_list)

    return panel