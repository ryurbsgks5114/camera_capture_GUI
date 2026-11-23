
import tkinter as tk
from tkinter import ttk

from config import WHITE, TEXT, BLUE

from common.ui.common import create_panel


def build(parent, app):
    """촬영 설정 UI를 생성합니다.

    Args:
        parent (tk.Widget): 촬영 설정 UI를 배치할 부모 위젯
        app (CameraManagerApp): 애플리케이션 인스턴스

    Returns:
        tuple: 촬영 설정 패널과 UI 잠금 함수
    """
    panel = create_panel(parent, "촬영 설정")
    panel.pack(fill="x", pady=(0, 5))

    time_row = tk.Frame(panel, bg=WHITE)
    time_row.pack(
        fill="x",
        padx=16,
        pady=(7, 3)
    )

    tk.Label(
        time_row,
        text="촬영 시작 시간",
        width=13,
        anchor="w",
        bg=WHITE,
        fg=TEXT,
        font=("Malgun Gothic", 9)
    ).pack(side="left")

    hour_entry = ttk.Spinbox(
        time_row,
        from_=0,
        to=23,
        increment=1,
        format="%02.0f",
        textvariable=app.state.hour_var,
        width=3,
        justify="center",
        validate="key",
        validatecommand=app.vcmd
    )
    hour_entry.pack(side="left")

    tk.Label(
        time_row,
        text=" : ",
        bg=WHITE,
        fg=TEXT,
        font=("Malgun Gothic", 10, "bold")
    ).pack(side="left")

    minute_entry = ttk.Spinbox(
        time_row,
        from_=0,
        to=59,
        increment=1,
        format="%02.0f",
        textvariable=app.state.minute_var,
        width=3,
        justify="center",
        validate="key",
        validatecommand=app.vcmd
    )
    minute_entry.pack(side="left")

    tk.Label(
        time_row,
        text=" : ",
        bg=WHITE,
        fg=TEXT,
        font=("Malgun Gothic", 10, "bold")
    ).pack(side="left")

    second_entry = ttk.Spinbox(
        time_row,
        from_=0,
        to=59,
        increment=1,
        format="%02.0f",
        textvariable=app.state.second_var,
        width=3,
        justify="center",
        validate="key",
        validatecommand=app.vcmd
    )
    second_entry.pack(side="left")

    tk.Label(
        time_row,
        text=" HH:MM:SS",
        bg=WHITE,
        fg="#607286",
        font=("Malgun Gothic", 8)
    ).pack(side="left")

    tk.Label(
        panel,
        text="※ 현재 시간이 설정 시간을 이미 지났다면 즉시 촬영이 시작됩니다.",
        bg=WHITE,
        fg=BLUE,
        justify="left",
        font=("Malgun Gothic", 8)
    ).pack(
        fill="x",
        padx=16,
        pady=(1, 4)
    )

    interval_row = tk.Frame(panel, bg=WHITE)
    interval_row.pack(
        fill="x",
        padx=16,
        pady=(3, 8)
    )

    tk.Label(
        interval_row,
        text="촬영 간격",
        width=13,
        anchor="w",
        bg=WHITE,
        fg=TEXT,
        font=("Malgun Gothic", 9)
    ).pack(side="left")

    interval_entry = ttk.Spinbox(
        interval_row,
        from_=1,
        to=100000,
        increment=1,
        textvariable=app.state.interval_var,
        width=6,
        justify="center",
        validate="key",
        validatecommand=app.vcmd
    )
    interval_entry.pack(side="left")

    tk.Label(
        interval_row,
        text=" 분",
        bg=WHITE,
        fg=TEXT,
        font=("Malgun Gothic", 9)
    ).pack(side="left")

    def set_capture_settings_locked(locked):
        """촬영 상태에 따라 촬영 설정 입력을 잠그거나 해제합니다.

        Args:
            locked (bool): True이면 입력을 잠그고 False이면 해제합니다.
        """
        new_state = "disabled" if locked else "normal"

        hour_entry.configure(state=new_state)
        minute_entry.configure(state=new_state)
        second_entry.configure(state=new_state)
        interval_entry.configure(state=new_state)

    return panel, set_capture_settings_locked
