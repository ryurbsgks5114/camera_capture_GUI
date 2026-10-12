import tkinter as tk

from config import WHITE, TEXT, GREEN, GRAY, RED
from ui.common import create_panel


def get_status_color(status):
    if status in ("연결됨", "촬영 중"):
        return GREEN
    if status == "연결 실패":
        return RED
    return GRAY


def build(parent, app):
    panel = create_panel(parent, "시스템 상태")
    panel.pack(fill="x", pady=(0, 10))

    app.system_body = tk.Frame(panel, bg=WHITE)
    app.system_body.pack(fill="x", padx=20, pady=8)

    refresh(app)
    return panel


def refresh(app):
    for widget in app.system_body.winfo_children():
        widget.destroy()

    statuses = [
        ("서버 연결 상태", app.state.server_status.get()),
        ("촬영 상태", app.state.capture_status.get()),
        ("FTP 연결 상태", app.state.ftp_status.get())
    ]

    for label, value in statuses:
        row = tk.Frame(app.system_body, bg=WHITE)
        row.pack(fill="x", pady=8)

        tk.Label(
            row, text=label, width=15, anchor="w",
            bg=WHITE, fg=TEXT, font=("Malgun Gothic", 10)
        ).pack(side="left")

        color = get_status_color(value)
        canvas = tk.Canvas(row, width=15, height=15, bg=WHITE, highlightthickness=0)
        canvas.pack(side="left", padx=(0, 7))
        canvas.create_oval(3, 3, 12, 12, fill=color, outline=color)

        tk.Label(
            row, text=value, bg=WHITE, fg=color,
            font=("Malgun Gothic", 10, "bold")
        ).pack(side="left")
