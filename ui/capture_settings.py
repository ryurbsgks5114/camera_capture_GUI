import tkinter as tk
from tkinter import ttk

from config import WHITE, TEXT, BLUE
from ui.common import create_panel


def build(parent, app):
    panel = create_panel(parent, "촬영 설정")
    panel.pack(fill="x", pady=(0, 5))

    time_row = tk.Frame(panel, bg=WHITE)
    time_row.pack(fill="x", padx=20, pady=5)

    tk.Label(
        time_row, text="촬영 시작 시간", width=15, anchor="w",
        bg=WHITE, fg=TEXT, font=("Malgun Gothic", 9)
    ).pack(side="left")

    hour_entry = ttk.Entry(
        time_row, textvariable=app.state.hour_var, width=3,
        justify="center", validate="key", validatecommand=app.vcmd
    )
    hour_entry.pack(side="left")

    tk.Label(time_row, text=" : ", bg=WHITE, fg=TEXT,
             font=("Malgun Gothic", 10, "bold")).pack(side="left")

    minute_entry = ttk.Entry(
        time_row, textvariable=app.state.minute_var, width=3,
        justify="center", validate="key", validatecommand=app.vcmd
    )
    minute_entry.pack(side="left")

    tk.Label(time_row, text=" : ", bg=WHITE, fg=TEXT,
             font=("Malgun Gothic", 10, "bold")).pack(side="left")

    second_entry = ttk.Entry(
        time_row, textvariable=app.state.second_var, width=3,
        justify="center", validate="key", validatecommand=app.vcmd
    )
    second_entry.pack(side="left")

    tk.Label(
        panel,
        text="※ 현재 시간이 설정 시간을 이미 지났다면 즉시 촬영이 시작됩니다.",
        bg=WHITE, fg=BLUE, justify="left", font=("Malgun Gothic", 8)
    ).pack(fill="x", padx=20, pady=(0, 8))

    interval_row = tk.Frame(panel, bg=WHITE)
    interval_row.pack(fill="x", padx=20, pady=5)

    tk.Label(
        interval_row, text="촬영 간격", width=15, anchor="w",
        bg=WHITE, fg=TEXT, font=("Malgun Gothic", 9)
    ).pack(side="left")

    ttk.Entry(
        interval_row, textvariable=app.state.interval_var,
        width=12, justify="right"
    ).pack(side="left")

    tk.Label(
        interval_row, text=" 분", bg=WHITE, fg=TEXT,
        font=("Malgun Gothic", 10)
    ).pack(side="left")

    def update(*args):
        app.state.start_time_display.set(
            app.state.hour_var.get() + ":" +
            app.state.minute_var.get() + ":" +
            app.state.second_var.get()
        )
        app.state.interval_display.set(app.state.interval_var.get() + " 분")

    app.state.hour_var.trace_add("write", update)
    app.state.minute_var.trace_add("write", update)
    app.state.second_var.trace_add("write", update)
    app.state.interval_var.trace_add("write", update)
