
import tkinter as tk

from common.ui.common import create_panel
from config import TEXT, WHITE


def build(parent, app):
    """저장 방식 설정 UI를 생성합니다.

    Args:
        parent (tk.Widget): 저장 방식 패널을 배치할 부모 위젯
        app (CameraManagerApp): 애플리케이션 인스턴스

    Returns:
        tuple: 생성된 패널과 UI 잠금 함수
    """
    options = {
        "ftp": "FTP 저장",
        "local": "로컬 저장",
        "both": "로컬 + FTP 저장"
    }

    def on_storage_mode_change(mode):
        """저장 방식 변경을 알림으로 표시합니다.

        Args:
            mode (str): 선택된 저장 방식
        """
        app.notify("저장 방식이 '{}'으로 설정되었습니다.".format(options.get(mode, "")))

    panel = create_panel(parent, "저장 방식")
    panel.pack(fill="x", pady=5)

    options_frame = tk.Frame(panel, bg=WHITE)
    options_frame.pack(fill="x", padx=18, pady=(5, 7))

    storage_radio_buttons = []

    for value, label in options.items():
        radio_button = tk.Radiobutton(
            options_frame,
            text=label,
            variable=app.state.storage_mode,
            value=value,
            command=lambda selected=value: on_storage_mode_change(selected),
            bg=WHITE,
            fg=TEXT,
            activebackground=WHITE,
            activeforeground=TEXT,
            selectcolor=WHITE,
            font=("Malgun Gothic", 9),
            anchor="w",
            padx=2,
            pady=1
        )
        radio_button.pack(fill="x", anchor="w", pady=1)
        storage_radio_buttons.append(radio_button)

    def set_storage_mode_locked(locked):
        """촬영 상태에 따라 저장 방식 선택을 잠그거나 해제합니다.

        Args:
            locked (bool): True이면 선택을 잠그고 False이면 해제합니다.
        """
        new_state = "disabled" if locked else "normal"

        for radio_button in storage_radio_buttons:
            radio_button.configure(state=new_state)

    return panel, set_storage_mode_locked
