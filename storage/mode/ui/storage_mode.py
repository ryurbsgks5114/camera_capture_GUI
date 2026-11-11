
import tkinter as tk

from config import WHITE, TEXT
from common.ui.common import create_panel


# ==========================================
# 저장 방식 설정 UI 및 기능
# ==========================================
def build(parent, app):
    mode_text = {
        "ftp": "FTP 저장",
        "local": "로컬 저장",
        "both": "로컬 + FTP 저장"
    }

    # 저장 방식 변경 알림
    def on_storage_mode_change(mode):
        app.notify(
            "저장 방식이 '{}'으로 설정되었습니다.".format(
                mode_text.get(mode, "")
            )
        )

    # 상위 패널 생성
    panel = create_panel(parent, "저장 방식")
    panel.pack(fill="x", pady=5)

    # 저장 방식 선택 영역
    options_frame = tk.Frame(
        panel,
        bg=WHITE
    )
    options_frame.pack(
        fill="x",
        padx=18,
        pady=(5, 7)
    )

    # 선택 가능한 저장 방식
    options = [
        ("ftp", "FTP 저장"),
        ("local", "로컬 저장"),
        ("both", "로컬 + FTP 저장")
    ]

    storage_radio_buttons = []

    # 라디오 버튼 생성
    for value, label in options:
        radio_button = tk.Radiobutton(
            options_frame,
            text=label,
            variable=app.state.storage_mode,
            value=value,
            command=lambda selected=value:
                on_storage_mode_change(selected),
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

        radio_button.pack(
            fill="x",
            anchor="w",
            pady=1
        )

        storage_radio_buttons.append(radio_button)

    # ==========================================
    # 촬영 중 저장 방식 선택 잠금 및 해제
    # ==========================================
    def set_storage_mode_locked(locked):
        new_state = "disabled" if locked else "normal"

        for radio_button in storage_radio_buttons:
            radio_button.configure(state=new_state)

    # 촬영 제어의 일괄 잠금 관리 목록에 등록
    app.capture_settings_lockers.append(
        set_storage_mode_locked
    )

    return panel
