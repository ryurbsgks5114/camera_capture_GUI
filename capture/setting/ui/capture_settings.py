
import tkinter as tk
from tkinter import ttk

from config import WHITE, TEXT, BLUE
from common.ui.common import create_panel


# ==========================================
# 촬영 설정 UI 및 기능
# ==========================================
def build(parent, app):
    panel = create_panel(parent, "촬영 설정")
    panel.pack(fill="x", pady=(0, 5))

    # ==========================================
    # 촬영 시작 시간 설정
    # ==========================================
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

    # 시 입력
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

    # 분 입력
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

    # 초 입력
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

    # 시간 형식 안내
    tk.Label(
        time_row,
        text=" HH:MM:SS",
        bg=WHITE,
        fg="#607286",
        font=("Malgun Gothic", 8)
    ).pack(side="left")

    # 기존 안내 문구 유지
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

    # ==========================================
    # 촬영 간격 설정
    # ==========================================
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

    # ==========================================
    # 촬영 중 설정 입력 잠금 및 해제
    # ==========================================
    def set_capture_settings_locked(locked):
        new_state = "disabled" if locked else "normal"

        hour_entry.configure(state=new_state)
        minute_entry.configure(state=new_state)
        second_entry.configure(state=new_state)
        interval_entry.configure(state=new_state)

    app.capture_settings_lockers.append(
        set_capture_settings_locked
    )

    return panel
