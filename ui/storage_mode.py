import tkinter as tk

from config import WHITE, TEXT
from ui.common import create_panel


def build(parent, app):
    def save():
        mode_text = {
            "both": "로컬 + FTP 저장",
            "local": "로컬 저장",
            "ftp": "FTP 저장"
        }
        app.notify(
            "저장 방식이 '" +
            mode_text.get(app.state.storage_mode.get(), "") +
            "'으로 설정되었습니다."
        )

    panel = create_panel(parent, "저장 방식", "저장", save)
    panel.pack(fill="x", pady=5)

    options = [
        ("both", "로컬 + FTP 저장"),
        ("local", "로컬 저장"),
        ("ftp", "FTP 저장")
    ]

    for value, label in options:
        tk.Radiobutton(
            panel, text=label, variable=app.state.storage_mode,
            value=value, bg=WHITE, fg=TEXT, activebackground=WHITE,
            selectcolor=WHITE, font=("Malgun Gothic", 10), anchor="w"
        ).pack(fill="x", padx=24, pady=5)
