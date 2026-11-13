
import threading
import tkinter as tk
import tkinter.font as tkfont

from tkinter import ttk

from config import (WHITE, TEXT, SUBTEXT, BLUE, GREEN, RED, GRAY)

from common.ui.common import create_panel

from camera.setting.service.camera_role_service import assign_camera_role

from camera.setting.api.camera_api import (get_cameras, get_camera_config, save_camera_config)


def build(parent, app):
    """카메라 설정 UI를 생성합니다.

    Args:
        parent (tk.Widget): 카메라 설정 UI를 배치할 부모 위젯
        app (CameraManagerApp): 애플리케이션 인스턴스

    Returns:
        tuple: 카메라 설정 패널과 입력 잠금 콜백
    """
    panel = create_panel(
        parent,
        "카메라 설정",
        "⟳  목록 새로고침",
        lambda: refresh_camera_list(),
    )
    panel.pack(fill="x", pady=5)

    body = tk.Frame(panel, bg=WHITE)
    body.pack(fill="x", padx=20, pady=10)

    combo_style = ttk.Style()

    combo_style.configure(
        "CameraRole.TCombobox",
        font=("Malgun Gothic", 9),
        padding=(8, 5),
        foreground=TEXT,
        background=WHITE,
        fieldbackground=WHITE,
        bordercolor="#D8E2EF",
        lightcolor="#D8E2EF",
        darkcolor="#D8E2EF",
        relief="solid",
        arrowsize=12,
    )

    combo_style.map(
        "CameraRole.TCombobox",
        fieldbackground=[
            ("readonly", WHITE),
            ("disabled", "#F5F7FA"),
        ],
        foreground=[
            ("readonly", TEXT),
            ("disabled", GRAY),
        ],
        selectbackground=[
            ("readonly", WHITE),
        ],
        selectforeground=[
            ("readonly", TEXT),
        ],
    )

    is_locked = False
    role_combos = []

    def set_camera_settings_locked(locked):
        """촬영 상태에 따라 카메라 설정 UI를 잠그거나 해제합니다.

        Args:
            locked (bool): True이면 카메라 설정을 비활성화합니다.
        """
        nonlocal is_locked

        is_locked = bool(locked)

        if panel.header_button:
            panel.header_button.configure(
                state="disabled" if is_locked else "normal",
                cursor="arrow" if is_locked else "hand2",
            )

        for combo in role_combos:
            if combo.winfo_exists():
                combo.configure(state="disabled" if is_locked else "readonly")

    status_label = tk.Label(
        body,
        text="카메라 목록을 확인하고 있습니다...",
        bg=WHITE,
        fg=GREEN,
        anchor="w",
        font=("Malgun Gothic", 9, "bold"),
    )
    status_label.pack(fill="x", pady=(0, 7))

    list_container = tk.Frame(body, bg=WHITE)
    list_container.pack(fill="x")

    camera_canvas = tk.Canvas(list_container, bg=WHITE, highlightthickness=0, height=140)
    camera_canvas.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(list_container, orient="vertical", command=camera_canvas.yview)
    scrollbar.pack(side="right", fill="y")

    camera_canvas.configure(yscrollcommand=scrollbar.set)

    camera_list_frame = tk.Frame(camera_canvas, bg=WHITE)

    camera_window = camera_canvas.create_window((0, 0), window=camera_list_frame, anchor="nw")

    def update_scroll_region(event=None):
        """카메라 목록의 스크롤 영역을 갱신합니다."""
        camera_canvas.configure(scrollregion=camera_canvas.bbox("all"))

    camera_list_frame.bind("<Configure>", update_scroll_region)

    camera_canvas.bind(
        "<Configure>",
        lambda event: camera_canvas.itemconfigure(
            camera_window,
            width=event.width,
        ),
    )

    def on_mousewheel(event):
        """마우스 휠 입력에 따라 카메라 목록을 스크롤합니다."""
        if not camera_canvas.winfo_exists():
            return "break"

        camera_canvas.yview_scroll(int(-1 * (event.delta / 120)),"units")

        return "break"

    def bind_scroll_to_widget(widget):
        """카메라 목록 내부 위젯에 마우스 휠 이벤트를 연결합니다.

        Args:
            widget (tk.Widget): 이벤트를 연결할 위젯
        """
        widget.bind("<MouseWheel>", on_mousewheel)

        for child in widget.winfo_children():
            bind_scroll_to_widget(child)

    camera_config = {
        "side_camera_id": None,
        "top_camera_id": None,
    }

    request_in_progress = False

    def change_camera_role(camera_id, selected_role):
        """선택한 카메라의 역할을 변경합니다.

        Args:
            camera_id (str): 역할을 변경할 카메라 ID
            selected_role (str): 지정할 역할
        """
        if is_locked:
            return

        if not camera_id:
            return

        if selected_role not in ("Side", "Top", "미지정"):
            return

        updated_config = assign_camera_role(camera_config, camera_id, selected_role)

        update_camera_config(
            updated_config["side_camera_id"],
            updated_config["top_camera_id"],
            "카메라 역할을 변경했습니다.",
        )

    def render_cameras(cameras):
        """조회된 카메라 목록을 화면에 표시합니다.

        Args:
            cameras (list): 조회된 카메라 정보 목록
        """
        role_combos.clear()

        for widget in camera_list_frame.winfo_children():
            widget.destroy()

        if not cameras:
            tk.Label(
                camera_list_frame,
                text="검색된 카메라가 없습니다.",
                bg=WHITE,
                fg=GRAY,
                anchor="w",
                font=("Malgun Gothic", 9),
            ).pack(fill="x", pady=8)

            update_scroll_region()
            bind_scroll_to_widget(camera_list_frame)

            return

        for index, camera in enumerate(cameras, start=1):
            if not isinstance(camera, dict):
                continue

            camera_id = camera.get("location_id")

            camera_name = str(camera.get("name") or "이름 없는 카메라")

            if camera_id == camera_config.get("side_camera_id"):
                current_role = "Side"
            elif camera_id == camera_config.get("top_camera_id"):
                current_role = "Top"
            else:
                current_role = "미지정"

            row = tk.Frame(
                camera_list_frame,
                bg=WHITE,
                highlightbackground="#D8E2EF",
                highlightthickness=1,
                height=52,
            )
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            content = tk.Frame(
                row,
                bg=WHITE,
            )
            content.pack(
                fill="both",
                expand=True,
                padx=12,
            )

            role_frame = tk.Frame(
                content,
                bg=WHITE,
            )
            role_frame.pack(side="right")

            tk.Label(
                role_frame,
                text="역할:",
                bg=WHITE,
                fg=SUBTEXT,
                font=("Malgun Gothic", 9),
            ).pack(side="left", padx=(0, 7))

            role_combo = ttk.Combobox(
                role_frame,
                values=("Side", "Top", "미지정"),
                state="disabled" if is_locked else "readonly",
                width=10,
                style="CameraRole.TCombobox",
            )
            role_combo.pack(side="left")

            role_combo.set(current_role)

            role_combos.append(role_combo)

            role_combo.bind(
                "<<ComboboxSelected>>",
                lambda event, cid=camera_id, combo=role_combo:
                    change_camera_role(
                        cid,
                        combo.get(),
                    ),
            )

            full_camera_text = "카메라 {}  |  {}".format(
                index,
                camera_name,
            )

            camera_font = tkfont.Font(
                family="Malgun Gothic",
                size=9,
                weight="bold",
            )

            camera_label = tk.Label(
                content,
                text=full_camera_text,
                bg=WHITE,
                fg=TEXT,
                anchor="w",
                font=camera_font,
            )
            camera_label.pack(
                side="left",
                fill="x",
                expand=True,
                padx=(0, 12),
            )

            def update_camera_name(event, label=camera_label, full_text=full_camera_text, font=camera_font):
                """위젯 너비에 맞춰 카메라 이름을 표시합니다.

                Args:
                    event (tk.Event): 위젯 크기 변경 이벤트
                    label (tk.Label): 카메라 이름 라벨
                    full_text (str): 원본 카메라 이름
                    font (tkfont.Font): 카메라 이름 표시 폰트
                """
                available_width = event.width

                if available_width <= 0:
                    return

                if font.measure(full_text) <= available_width:
                    display_text = full_text
                else:
                    ellipsis = "..."

                    if font.measure(ellipsis) > available_width:
                        display_text = ""
                    else:
                        left = 0
                        right = len(full_text)

                        while left < right:
                            middle = (left + right + 1) // 2
                            candidate = full_text[:middle] + ellipsis

                            if font.measure(candidate) <= available_width:
                                left = middle
                            else:
                                right = middle - 1

                        display_text = full_text[:left] + ellipsis

                if label.cget("text") != display_text:
                    label.configure(text=display_text)

            camera_label.bind("<Configure>", update_camera_name)

            role_combo.bind("<MouseWheel>", on_mousewheel)

        update_scroll_region()
        bind_scroll_to_widget(camera_list_frame)

    def finish_request(cameras, config, error_message, notice=None):
        """카메라 요청 결과를 화면에 반영합니다.

        Args:
            cameras (list): 조회된 카메라 목록
            config (dict): 조회된 카메라 역할 설정
            error_message (str): 요청 실패 메시지
            notice (str, optional): 요청 성공 시 표시할 알림
        """
        nonlocal request_in_progress
        nonlocal camera_config

        request_in_progress = False

        if not panel.winfo_exists():
            return

        if error_message is not None:
            status_label.configure(text="카메라 설정 처리에 실패했습니다.", fg=RED)

            app.notify(error_message, RED)

            return

        camera_config = config or {
            "side_camera_id": None,
            "top_camera_id": None,
        }

        status_label.configure(text="검색된 카메라: {}대".format(len(cameras)), fg=GREEN)

        render_cameras(cameras)

        if notice:
            app.notify(notice, GREEN)

    def refresh_camera_list():
        """카메라 목록과 현재 역할 설정을 조회합니다."""
        nonlocal request_in_progress

        if is_locked:
            return

        if request_in_progress:
            return

        request_in_progress = True

        status_label.configure(text="카메라 목록을 확인하고 있습니다...", fg=BLUE)

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
                        error_message,
                    ),
                )
            except tk.TclError:
                pass

        threading.Thread(
            target=worker,
            name="CameraListRequestThread",
            daemon=True,
        ).start()

    def update_camera_config(side_camera_id, top_camera_id, notice):
        """변경된 카메라 역할을 서버에 저장하고 목록을 갱신합니다.

        Args:
            side_camera_id (str): Side 카메라 ID
            top_camera_id (str): Top 카메라 ID
            notice (str): 저장 성공 시 표시할 알림
        """
        nonlocal request_in_progress

        if is_locked:
            return

        if request_in_progress:
            return

        request_in_progress = True

        status_label.configure(text="카메라 역할을 변경하고 있습니다...", fg=BLUE)

        def worker():
            try:
                save_camera_config(side_camera_id, top_camera_id)

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
                        notice if error_message is None else None,
                    ),
                )
            except tk.TclError:
                pass

        threading.Thread(
            target=worker,
            name="CameraConfigRequestThread",
            daemon=True,
        ).start()

    app.root.after(100, refresh_camera_list)

    return panel, set_camera_settings_locked
