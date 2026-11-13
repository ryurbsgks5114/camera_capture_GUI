
import io
import tkinter as tk

from PIL import Image, ImageTk

from config import (WHITE, TEXT, SUBTEXT, BLUE, GREEN, RED, GRAY, GRAY_LIGHT, BORDER)

from common.ui.common import create_panel

from camera.preview.service.camera_preview_service import CameraPreviewService


def build(parent, app):
    """카메라 실시간 미리보기 UI를 생성합니다.

    Args:
        parent (tk.Widget): 미리보기 UI를 배치할 부모 위젯
        app (CameraManagerApp): 애플리케이션 인스턴스

    Returns:
        tk.Frame: 생성된 미리보기 패널
    """
    panel = create_panel(parent, "카메라 실시간 미리보기")
    panel.pack(fill="x", expand=False, pady=(0, 5))

    status_label = tk.Label(
        panel,
        text="미리보기 대기 중",
        bg=WHITE,
        fg=SUBTEXT,
        font=("Malgun Gothic", 9),
    )
    status_label.pack(
        anchor="w",
        padx=20,
        pady=(8, 5),
    )

    button_frame = tk.Frame(panel, bg=WHITE)
    button_frame.pack(fill="x", padx=12, pady=(0, 5))

    app.preview_widgets = {}

    preview_running = False

    preview_service = CameraPreviewService(schedule_callback=app.root.after)

    def create_preview_area(view, title):
        """개별 카메라의 미리보기 영역을 생성합니다.

        Args:
            view (str): 카메라 구분값
            title (str): 화면에 표시할 카메라 이름

        Returns:
            dict: 미리보기 이미지 위젯과 이미지 참조
        """
        camera_frame = tk.Frame(
            panel,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1,
        )
        camera_frame.pack(
            fill="x",
            padx=12,
            pady=5,
        )

        tk.Label(
            camera_frame,
            text=title,
            bg=WHITE,
            fg=TEXT,
            font=("Malgun Gothic", 10, "bold"),
            anchor="w",
        ).pack(
            fill="x",
            padx=10,
            pady=(7, 5),
        )

        image_label = tk.Label(
            camera_frame,
            text="미리보기 대기 중",
            bg=GRAY_LIGHT,
            fg=SUBTEXT,
            font=("Malgun Gothic", 10),
            anchor="center",
            width=40,
            height=10,
        )
        image_label.pack(
            fill="x",
            padx=10,
            pady=(0, 10),
        )

        return {
            "image_label": image_label,
            "photo": None,
        }

    app.preview_widgets["side"] = create_preview_area("side", "측면 카메라 (Side)")
    app.preview_widgets["top"] = create_preview_area("top", "상단 카메라 (Top)")

    def update_preview_image(view, frame_data):
        """전달받은 JPEG 프레임을 화면에 표시합니다.

        Args:
            view (str): 카메라 구분값
            frame_data (bytes): JPEG 이미지 데이터
        """
        widgets = app.preview_widgets.get(view)

        if not widgets or not frame_data:
            return

        try:
            with Image.open(io.BytesIO(frame_data)) as source:
                image = source.convert("RGB")

            resampling = getattr(Image, "Resampling", Image)

            image.thumbnail((480, 270), resampling.LANCZOS)

            photo = ImageTk.PhotoImage(image)

            image_label = widgets["image_label"]

            image_label.configure(
                image=photo,
                text="",
                width=0,
                height=0,
            )

            widgets["photo"] = photo
            image_label.image = photo
        except (OSError, ValueError) as error:
            print("{} 카메라 프레임 표시 실패: {}".format(view, error))

    def handle_preview_frames(frames):
        """조회된 Side와 Top 프레임을 화면에 반영합니다.

        Args:
            frames (dict): 카메라별 JPEG 프레임 데이터
        """
        if not preview_running:
            return

        status_label.configure(text="카메라 미리보기 실행 중", fg=GREEN)

        for view, frame_data in frames.items():
            if frame_data:
                update_preview_image(view, frame_data)

    def handle_frame_error(message):
        """프레임 조회 실패 상태를 화면에 표시합니다.

        Args:
            message (str): 프레임 조회 실패 메시지
        """
        if not preview_running:
            return

        status_label.configure(text="미리보기 연결 오류", fg=RED)

        app.notify("카메라 미리보기 프레임을 가져오지 못했습니다: {}".format(message), RED)

    def handle_start_success(response):
        """미리보기 시작 성공 결과를 화면에 반영합니다.

        Args:
            response (dict): 서버 응답 데이터
        """
        nonlocal preview_running

        preview_running = True

        start_button.configure(state=tk.DISABLED, text="미리보기 실행 중")

        stop_button.configure(state=tk.NORMAL, text="■  미리보기 중지")

        status_label.configure(text="카메라 미리보기 실행 중", fg=GREEN)

        message = (
            response.get("message", "카메라 미리보기를 시작했습니다.")
            if isinstance(response, dict)
            else "카메라 미리보기를 시작했습니다."
        )

        app.notify(message, GREEN)

    def handle_start_failure(message):
        """미리보기 시작 실패 결과를 화면에 반영합니다.

        Args:
            message (str): 시작 실패 메시지
        """
        start_button.configure(state=tk.NORMAL, text="▶  미리보기 시작")

        stop_button.configure(state=tk.DISABLED, text="■  미리보기 중지")

        status_label.configure(text="미리보기 시작 실패", fg=RED)

        app.notify("카메라 미리보기를 시작하지 못했습니다: {}".format(message), RED)

    def handle_stop_success(response):
        """미리보기 중지 성공 결과를 화면에 반영합니다.

        Args:
            response (dict): 서버 응답 데이터
        """
        start_button.configure(state=tk.NORMAL, text="▶  미리보기 시작")

        stop_button.configure(state=tk.DISABLED, text="■  미리보기 중지")

        status_label.configure(text="미리보기 대기 중", fg=SUBTEXT)

        for widgets in app.preview_widgets.values():
            image_label = widgets["image_label"]

            image_label.configure(
                image="",
                text="미리보기 대기 중",
                width=40,
                height=10,
            )

            image_label.image = None
            widgets["photo"] = None

        message = (
            response.get("message", "카메라 미리보기를 중지했습니다.")
            if isinstance(response, dict)
            else "카메라 미리보기를 중지했습니다."
        )

        app.notify(message, GREEN)

    def handle_stop_failure(message):
        """미리보기 중지 실패 결과를 화면에 반영합니다.

        Args:
            message (str): 중지 실패 메시지
        """
        nonlocal preview_running

        preview_running = True

        start_button.configure(state=tk.DISABLED, text="미리보기 실행 중")

        stop_button.configure(state=tk.NORMAL, text="■  미리보기 중지")

        status_label.configure(text="미리보기 중지 실패", fg=RED)

        app.notify("카메라 미리보기 중지에 실패했습니다: {}".format(message), RED)

    def start_preview():
        """미리보기 시작을 요청하고 UI 상태를 갱신합니다."""
        if preview_running:
            return

        start_button.configure(state=tk.DISABLED, text="미리보기 시작 중...")

        status_label.configure(text="카메라 미리보기를 시작하고 있습니다...", fg=BLUE)

        app.notify("카메라 미리보기를 시작하고 있습니다...", BLUE)

        preview_service.start_preview(
            on_success=handle_start_success,
            on_error=handle_start_failure,
            on_frames=handle_preview_frames,
            on_frame_error=handle_frame_error,
        )

    def stop_preview():
        """미리보기 중지를 요청하고 UI 상태를 갱신합니다."""
        nonlocal preview_running

        if not preview_running:
            return

        preview_running = False

        stop_button.configure(state=tk.DISABLED, text="중지 중...")

        status_label.configure(text="카메라 미리보기를 중지하고 있습니다...", fg=BLUE)

        preview_service.stop_preview(
            on_success=handle_stop_success,
            on_error=handle_stop_failure,
        )

    start_button = tk.Button(
        button_frame,
        text="▶  미리보기 시작",
        command=start_preview,
        bg=BLUE,
        fg=WHITE,
        activebackground=BLUE,
        activeforeground=WHITE,
        disabledforeground=WHITE,
        relief="flat",
        bd=0,
        font=("Malgun Gothic", 9, "bold"),
        pady=8,
    )
    start_button.pack(
        side="left",
        fill="x",
        expand=True,
        padx=(0, 4),
    )

    stop_button = tk.Button(
        button_frame,
        text="■  미리보기 중지",
        command=stop_preview,
        state=tk.DISABLED,
        bg=GRAY,
        fg=WHITE,
        activebackground=GRAY,
        activeforeground=WHITE,
        disabledforeground=WHITE,
        relief="flat",
        bd=0,
        font=("Malgun Gothic", 9, "bold"),
        pady=8,
    )
    stop_button.pack(
        side="left",
        fill="x",
        expand=True,
        padx=(4, 0),
    )

    app.preview_status_label = status_label
    app.preview_start_button = start_button
    app.preview_stop_button = stop_button

    return panel
