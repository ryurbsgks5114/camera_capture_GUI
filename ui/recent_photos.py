import tkinter as tk

from config import BG, SUBTEXT
from ui.common import create_panel


def build(parent, app):
    panel = create_panel(parent, "최근 촬영 사진")
    panel.pack(fill="both", expand=True, pady=(0, 10))

    area = tk.Frame(
        panel, bg="#F7FAFF",
        highlightbackground="#CFDBEB", highlightthickness=1
    )
    area.pack(fill="both", expand=True, padx=18, pady=18)

    tk.Label(
        area, text="▧", bg="#F7FAFF", fg="#B0BFD1",
        font=("Arial", 42)
    ).pack(expand=True, pady=(30, 0))

    tk.Label(
        area,
        text=("최근 촬영된 사진이 여기에 표시됩니다.\n"
              "(추후 기능 확정 예정)"),
        bg="#F7FAFF", fg=SUBTEXT,
        font=("Malgun Gothic", 9), justify="center"
    ).pack(expand=True, pady=(0, 30))
