
import tkinter as tk

from config import WHITE, BLUE, GRAY_LIGHT, SUBTEXT

from common.ui.common import create_panel


class CameraPreviewUI:
    """카메라 미리보기 패널 UI를 관리합니다."""
    VIEW_LABELS = {
        "side": "측면 카메라 (Side)",
        "top": "상단 카메라 (Top)"
    }

    PREVIEW_AREA_HEIGHT = 44

    def __init__(self, parent):
        """카메라 미리보기 UI를 초기화합니다.

        Args:
            parent (tk.Widget): 미리보기 패널을 배치할 부모 위젯
        """
        self._on_preview_requested = None
        self._camera_roles = {}

        self.panel = create_panel(parent, "카메라 미리보기")
        self.panel.pack(
            fill="x",
            expand=False,
            pady=(0, 5)
        )

        self._build_content()

    def _build_content(self):
        """미리보기 표시 영역을 생성합니다."""
        self.content_frame = tk.Frame(
            self.panel,
            bg=WHITE
        )
        self.content_frame.pack(
            fill="x",
            padx=12,
            pady=7
        )

        # 안내 문구와 미리보기 버튼이 동일한 영역을 사용합니다.
        self.preview_area = tk.Frame(
            self.content_frame,
            bg=GRAY_LIGHT,
            height=self.PREVIEW_AREA_HEIGHT
        )
        self.preview_area.pack(fill="x")
        self.preview_area.pack_propagate(False)

        self.empty_label = tk.Label(
            self.preview_area,
            text="현재 연결된 카메라가 없습니다.",
            bg=GRAY_LIGHT,
            fg=SUBTEXT,
            font=("Malgun Gothic", 9),
            anchor="center"
        )
        self.empty_label.pack(
            fill="both",
            expand=True
        )

        self._preview_buttons = {}

    def set_preview_handler(self, callback):
        """미리보기 요청 이벤트를 외부 관리자와 연결합니다.

        Args:
            callback (callable): 미리보기 요청 시 실행할 콜백
        """
        self._on_preview_requested = callback

    def update_camera_roles(self, camera_config, available_camera_ids):
        """실제 연결된 카메라와 저장된 역할 설정을 반영합니다.

        Args:
            camera_config (dict): Side와 Top 카메라 ID 설정
            available_camera_ids (iterable): 실제 검색된 카메라 ID 목록
        """
        camera_config = camera_config or {}
        available_camera_ids = set(available_camera_ids or [])

        self._camera_roles.clear()

        for view in self.VIEW_LABELS:
            camera_id = camera_config.get("{}_camera_id".format(view))

            if camera_id and camera_id in available_camera_ids:
                self._camera_roles[view] = camera_id

        self._render_preview_area()

    def _render_preview_area(self):
        """카메라 설정에 따라 안내 문구 또는 버튼을 표시합니다."""
        for button in self._preview_buttons.values():
            button.destroy()

        self._preview_buttons.clear()

        if not self._camera_roles:
            self.empty_label.pack(
                fill="both",
                expand=True
            )

            return

        self.empty_label.pack_forget()

        available_views = [
            view
            for view in self.VIEW_LABELS
            if view in self._camera_roles
        ]

        for index, view in enumerate(available_views):
            button = tk.Button(
                self.preview_area,
                text=self.VIEW_LABELS[view],
                command=lambda selected_view=view:
                    self._request_preview(selected_view),
                bg=BLUE,
                fg=WHITE,
                activebackground=BLUE,
                activeforeground=WHITE,
                relief="flat",
                bd=0,
                font=("Malgun Gothic", 9, "bold"),
                pady=6,
                cursor="hand2"
            )

            button.pack(
                side="left",
                fill="both",
                expand=True,
                padx=(
                    (4, 2)
                    if index == 0 and len(available_views) == 2
                    else (2, 4)
                    if index == 1
                    else 0
                ),
                pady=0
            )

            self._preview_buttons[view] = button

    def _request_preview(self, view):
        """선택한 카메라의 미리보기 요청을 외부로 전달합니다.

        Args:
            view (str): 카메라 구분값 (side 또는 top)
        """
        if view not in self._camera_roles:
            return

        if self._on_preview_requested is None:
            return

        self._on_preview_requested(view)


def build(parent, app):
    """카메라 미리보기 UI를 생성합니다.

    Args:
        parent (tk.Widget): 미리보기 UI를 배치할 부모 위젯
        app (CameraManagerApp): 애플리케이션 인스턴스

    Returns:
        CameraPreviewUI: 생성된 미리보기 UI 객체
    """
    return CameraPreviewUI(parent)
