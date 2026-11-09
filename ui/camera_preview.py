
import io
import threading
import tkinter as tk

from PIL import Image, ImageTk

from config import (
    WHITE,
    TEXT,
    SUBTEXT,
    BLUE,
    BLUE_LIGHT,
    GREEN,
    RED,
    GRAY,
    GRAY_LIGHT,
    BORDER
)

from services.api_client import (
    start_preview as request_start_preview,
    stop_preview as request_stop_preview,
    get_preview_frame
)

from ui.common import create_panel


# ==========================================
# 카메라 실시간 미리보기 UI 생성 함수
# ==========================================
def build(parent, app):

    # 상위 패널 생성
    panel = create_panel(parent, "카메라 실시간 미리보기")
    panel.pack(fill="x", expand=False, pady=(0, 5))

    # 미리보기 상태 표시 영역
    status_label = tk.Label(
        panel,
        text="미리보기 대기 중",
        bg=WHITE,
        fg=SUBTEXT,
        font=("Malgun Gothic", 9)
    )
    status_label.pack(
        anchor="w",
        padx=20,
        pady=(8, 5)
    )

    # 미리보기 시작 / 중지 버튼 영역
    button_frame = tk.Frame(panel, bg=WHITE)
    button_frame.pack(
        fill="x",
        padx=12,
        pady=(0, 5)
    )

    # Side / Top 카메라 미리보기 위젯 저장
    app.preview_widgets = {}

    # 미리보기 동작 상태
    preview_running = False
    preview_requesting = False

    # 프레임 요청 중 오류 알림 중복 방지
    frame_error_reported = False

    # ==========================================
    # 개별 카메라 미리보기 영역 생성
    # ==========================================
    def create_preview_area(view, title):

        camera_frame = tk.Frame(
            panel,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        camera_frame.pack(
            fill="x",
            padx=12,
            pady=5
        )

        # 카메라 이름
        tk.Label(
            camera_frame,
            text=title,
            bg=WHITE,
            fg=TEXT,
            font=("Malgun Gothic", 10, "bold"),
            anchor="w"
        ).pack(
            fill="x",
            padx=10,
            pady=(7, 5)
        )

        # 실제 영상 표시 영역
        image_label = tk.Label(
            camera_frame,
            text="미리보기 대기 중",
            bg=GRAY_LIGHT,
            fg=SUBTEXT,
            font=("Malgun Gothic", 10),
            anchor="center",
            width=40,
            height=10
        )
        image_label.pack(
            fill="x",
            padx=10,
            pady=(0, 10)
        )

        return {
            "image_label": image_label,
            "photo": None
        }

    # 측면 카메라 미리보기
    app.preview_widgets["side"] = create_preview_area(
        "side",
        "측면 카메라 (Side)"
    )

    # 상단 카메라 미리보기
    app.preview_widgets["top"] = create_preview_area(
        "top",
        "상단 카메라 (Top)"
    )

    # ==========================================
    # 전달받은 JPEG 프레임을 화면에 표시
    # ==========================================
    def update_preview_image(view, frame_data):

        widgets = app.preview_widgets.get(view)

        if not widgets or not frame_data:
            return

        try:
            # JPEG 바이트 데이터를 Pillow 이미지로 변환
            with Image.open(io.BytesIO(frame_data)) as source:
                image = source.convert("RGB")

            # GUI 표시 영역에 맞게 이미지 크기 조절
            # 원본 비율은 유지하고 서버에서 받은 원본 크기는 변경하지 않음
            resampling = getattr(Image, "Resampling", Image)

            image.thumbnail(
                (480, 270),
                resampling.LANCZOS
            )

            # Tkinter에서 사용할 이미지 객체 생성
            photo = ImageTk.PhotoImage(image)

            image_label = widgets["image_label"]

            image_label.configure(
                image=photo,
                text="",
                width=0,
                height=0
            )

            # 이미지 객체 참조 유지
            widgets["photo"] = photo
            image_label.image = photo

        except (OSError, ValueError) as error:
            print(
                "{} 카메라 프레임 표시 실패: {}".format(
                    view,
                    error
                )
            )

    # ==========================================
    # 미리보기 프레임 요청 결과 처리
    # ==========================================
    def handle_preview_frames(frames, error=None):

        nonlocal frame_error_reported

        if not preview_running:
            return

        if error:
            status_label.configure(
                text="미리보기 연결 오류",
                fg=RED
            )

            if not frame_error_reported:
                frame_error_reported = True
                app.notify(
                    "카메라 미리보기 프레임을 가져오지 못했습니다: {}".format(error),
                    RED
                )

            return

        frame_error_reported = False

        # 각 카메라 영상 갱신
        for view, frame_data in frames.items():

            if frame_data:
                update_preview_image(view, frame_data)

    # ==========================================
    # 서버에서 Side / Top 프레임 가져오기
    # ==========================================
    def fetch_preview_frames():

        nonlocal preview_requesting

        if not preview_running or preview_requesting:
            return

        preview_requesting = True

        def request_frames():

            nonlocal preview_requesting

            frames = {}
            error_message = None

            try:
                # Side 카메라 프레임 요청
                frames["side"] = get_preview_frame("side")

                # Top 카메라 프레임 요청
                frames["top"] = get_preview_frame("top")

            except Exception as error:
                error_message = str(error)

            finally:
                preview_requesting = False

            # Tkinter 화면 갱신은 메인 스레드에서 실행
            try:
                app.root.after(
                    0,
                    lambda frames=frames, error=error_message:
                    handle_preview_frames(frames, error)
                )
            except RuntimeError:
                pass

        threading.Thread(
            target=request_frames,
            name="CameraPreviewFrameThread",
            daemon=True
        ).start()

        # 약 5 FPS 간격으로 프레임 요청
        app.root.after(200, fetch_preview_frames)

    # ==========================================
    # 미리보기 시작 요청
    # ==========================================
    def start_preview():

        nonlocal preview_running

        if preview_running:
            return

        start_button.configure(
            state=tk.DISABLED,
            text="미리보기 시작 중..."
        )

        status_label.configure(
            text="카메라 미리보기를 시작하고 있습니다...",
            fg=BLUE
        )

        app.notify(
            "카메라 미리보기를 시작하고 있습니다...",
            BLUE
        )

        def send_start_request():

            try:
                response = request_start_preview()

            except Exception as error:
                app.root.after(
                    0,
                    lambda error=str(error): handle_start_failure(error)
                )
                return

            app.root.after(
                0,
                lambda response=response: handle_start_success(response)
            )

        threading.Thread(
            target=send_start_request,
            name="CameraPreviewStartThread",
            daemon=True
        ).start()

    # ==========================================
    # 미리보기 시작 성공 처리
    # ==========================================
    def handle_start_success(response):

        nonlocal preview_running
        nonlocal frame_error_reported

        preview_running = True
        frame_error_reported = False

        start_button.configure(
            state=tk.DISABLED,
            text="미리보기 실행 중"
        )

        stop_button.configure(
            state=tk.NORMAL
        )

        status_label.configure(
            text="카메라 미리보기 실행 중",
            fg=GREEN
        )

        message = (
            response.get("message", "카메라 미리보기를 시작했습니다.")
            if isinstance(response, dict)
            else "카메라 미리보기를 시작했습니다."
        )

        app.notify(message, GREEN)

        # 첫 번째 프레임 요청 시작
        fetch_preview_frames()

    # ==========================================
    # 미리보기 시작 실패 처리
    # ==========================================
    def handle_start_failure(message):

        start_button.configure(
            state=tk.NORMAL,
            text="▶  미리보기 시작"
        )

        stop_button.configure(
            state=tk.DISABLED
        )

        status_label.configure(
            text="미리보기 시작 실패",
            fg=RED
        )

        app.notify(
            "카메라 미리보기를 시작하지 못했습니다: {}".format(message),
            RED
        )

    # ==========================================
    # 미리보기 중지 요청
    # ==========================================
    def stop_preview():

        nonlocal preview_running

        if not preview_running:
            return

        # 프레임 요청 중단
        preview_running = False

        stop_button.configure(
            state=tk.DISABLED,
            text="중지 중..."
        )

        status_label.configure(
            text="카메라 미리보기를 중지하고 있습니다...",
            fg=BLUE
        )

        def send_stop_request():

            try:
                response = request_stop_preview()

            except Exception as error:
                app.root.after(
                    0,
                    lambda error=str(error): handle_stop_failure(error)
                )
                return

            app.root.after(
                0,
                lambda response=response: handle_stop_success(response)
            )

        threading.Thread(
            target=send_stop_request,
            name="CameraPreviewStopThread",
            daemon=True
        ).start()

    # ==========================================
    # 미리보기 중지 성공 처리
    # ==========================================
    def handle_stop_success(response):

        start_button.configure(
            state=tk.NORMAL,
            text="▶  미리보기 시작"
        )

        stop_button.configure(
            state=tk.DISABLED,
            text="■  미리보기 중지"
        )

        status_label.configure(
            text="미리보기 대기 중",
            fg=SUBTEXT
        )

        # 화면에 표시된 기존 프레임 제거
        for widgets in app.preview_widgets.values():

            image_label = widgets["image_label"]

            image_label.configure(
                image="",
                text="미리보기 대기 중",
                width=40,
                height=10
            )

            image_label.image = None
            widgets["photo"] = None

        message = (
            response.get("message", "카메라 미리보기를 중지했습니다.")
            if isinstance(response, dict)
            else "카메라 미리보기를 중지했습니다."
        )

        app.notify(message, GREEN)

    # ==========================================
    # 미리보기 중지 실패 처리
    # ==========================================
    def handle_stop_failure(message):

        nonlocal preview_running

        preview_running = True

        start_button.configure(
            state=tk.DISABLED,
            text="미리보기 실행 중"
        )

        stop_button.configure(
            state=tk.NORMAL,
            text="■  미리보기 중지"
        )

        status_label.configure(
            text="미리보기 중지 실패",
            fg=RED
        )

        app.notify(
            "카메라 미리보기 중지에 실패했습니다: {}".format(message),
            RED
        )

        # 프레임 요청 재개
        fetch_preview_frames()

    # ==========================================
    # 미리보기 버튼 생성
    # ==========================================
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
        pady=8
    )
    start_button.pack(
        side="left",
        fill="x",
        expand=True,
        padx=(0, 4)
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
        pady=8
    )
    stop_button.pack(
        side="left",
        fill="x",
        expand=True,
        padx=(4, 0)
    )

    # 상태 레이블 및 버튼 참조 저장
    app.preview_status_label = status_label
    app.preview_start_button = start_button
    app.preview_stop_button = stop_button

    return panel
