
import io
import tkinter as tk

from PIL import Image, ImageTk, UnidentifiedImageError

from config import GRAY_LIGHT, SUBTEXT


class PreviewWindow:
    """카메라 미리보기 이미지를 표시하는 독립 창을 관리합니다."""
    VIEW_TITLES = {
        "side": "측면 카메라 미리보기",
        "top": "상단 카메라 미리보기"
    }

    DEFAULT_WIDTH = 1600
    DEFAULT_HEIGHT = 900
    MIN_WIDTH = 960
    MIN_HEIGHT = 540
    SCREEN_MARGIN_WIDTH = 80
    SCREEN_MARGIN_HEIGHT = 120

    def __init__(self, parent, view, on_close):
        """미리보기 창을 초기화합니다.

        Args:
            parent (tk.Widget): 미리보기 창의 부모 위젯
            view (str): 카메라 구분값 (side 또는 top)
            on_close (callable): 창이 닫힐 때 호출할 콜백
        """
        if view not in self.VIEW_TITLES:
            raise ValueError("잘못된 카메라 구분입니다.")

        self._parent = parent
        self._view = view
        self._on_close = on_close

        self._window = tk.Toplevel(parent)
        self._window.title(self.VIEW_TITLES[view])
        self._window.configure(bg=GRAY_LIGHT)

        self._original_image = None
        self._photo_image = None
        self._resize_job = None
        self._closed = False

        self._configure_window_size()
        self._create_widgets()

        self._window.protocol(
            "WM_DELETE_WINDOW",
            self._handle_close
        )

        self._window.bind(
            "<Configure>",
            self._handle_resize
        )

    def _configure_window_size(self):
        """화면 크기에 맞춰 초기 창 크기와 위치를 설정합니다."""
        screen_width = self._window.winfo_screenwidth()
        screen_height = self._window.winfo_screenheight()

        available_width = max(1, screen_width - self.SCREEN_MARGIN_WIDTH)
        available_height = max(1, screen_height - self.SCREEN_MARGIN_HEIGHT)

        window_width = min(self.DEFAULT_WIDTH, available_width)
        window_height = min(self.DEFAULT_HEIGHT, available_height)

        min_width = min(self.MIN_WIDTH, window_width)
        min_height = min(self.MIN_HEIGHT, window_height)

        position_x = max(0, (screen_width - window_width) // 2)
        position_y = max(0, (screen_height - window_height) // 2)

        self._window.geometry("{}x{}+{}+{}".format(window_width, window_height, position_x, position_y))

        self._window.minsize(min_width, min_height)

    def _create_widgets(self):
        """미리보기 이미지 표시 영역을 생성합니다."""
        self._preview_label = tk.Label(
            self._window,
            bg=GRAY_LIGHT,
            fg=SUBTEXT,
            text="카메라 연결 중...",
            anchor="center"
        )

        self._preview_label.pack(
            fill="both",
            expand=True
        )

    def update_frame(self, frame_bytes):
        """전달받은 카메라 프레임을 표시합니다.

        Args:
            frame_bytes (bytes): JPEG 이미지 데이터
        """
        if self._closed or not frame_bytes:
            return

        try:
            image = Image.open(io.BytesIO(frame_bytes))
            image.load()

            self._original_image = image.convert("RGB")

            self._render_image()
        except (UnidentifiedImageError, OSError, ValueError):
            self._preview_label.configure(
                image="",
                text="이미지를 표시할 수 없습니다."
            )

            self._photo_image = None
            self._original_image = None

    def _handle_resize(self, event):
        """창 크기 변경 시 이미지 렌더링을 예약합니다.

        Args:
            event (tk.Event): 창 크기 변경 이벤트
        """
        if self._closed or event.widget != self._window:
            return

        if self._resize_job is not None:
            self._window.after_cancel(self._resize_job)

        self._resize_job = self._window.after(100, self._render_image)

    def _render_image(self):
        """원본 비율을 유지하면서 표시 영역에 맞게 이미지를 조정합니다."""
        self._resize_job = None

        if self._closed or self._original_image is None:
            return

        area_width = self._preview_label.winfo_width()
        area_height = self._preview_label.winfo_height()

        if area_width <= 1 or area_height <= 1:
            return

        original_width, original_height = self._original_image.size

        if original_width <= 0 or original_height <= 0:
            return

        scale = min(area_width / original_width, area_height / original_height)

        display_width = max(1, int(original_width * scale))
        display_height = max(1, int(original_height * scale))

        resized_image = self._original_image.resize(
            (display_width, display_height),
            Image.Resampling.LANCZOS
        )

        self._photo_image = ImageTk.PhotoImage(resized_image)

        self._preview_label.configure(
            image=self._photo_image,
            text=""
        )

    def _handle_close(self):
        """사용자가 창을 닫을 때 관리자에게 알립니다."""
        if self._closed:
            return

        if self._on_close is not None:
            self._on_close(self._view)

    def close(self):
        """미리보기 창을 정리하고 닫습니다."""
        if self._closed:
            return

        self._closed = True

        if self._resize_job is not None:
            try:
                self._window.after_cancel(self._resize_job)
            except tk.TclError:
                pass

            self._resize_job = None

        try:
            if self._window.winfo_exists():
                self._window.destroy()
        except tk.TclError:
            pass

        self._original_image = None
        self._photo_image = None
