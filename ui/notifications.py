import tkinter as tk
from tkinter import ttk
from datetime import datetime

from config import WHITE, GRAY, TEXT
from ui.common import create_panel


def build(parent, app):
    panel = create_panel(parent, "알림")
    panel.pack(fill="both", expand=True, pady=5)

    area = tk.Frame(panel, bg=WHITE)
    area.pack(fill="both", expand=True, padx=18, pady=10)

    canvas = tk.Canvas(area, bg=WHITE, highlightthickness=0)
    scrollbar = ttk.Scrollbar(area, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    notice_list = tk.Frame(canvas, bg=WHITE)
    window = canvas.create_window((0, 0), window=notice_list, anchor="nw")

    def update_scrollregion(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def resize_list(event):
        canvas.itemconfigure(window, width=event.width)

    notice_list.bind("<Configure>", update_scrollregion)
    canvas.bind("<Configure>", resize_list)

    def add_notice(message, color=TEXT):
        now = datetime.now().strftime("%H:%M:%S")

        row = tk.Frame(notice_list, bg=WHITE)
        row.pack(fill="x", pady=5)

        tk.Label(
            row, text=now, bg=WHITE, fg=GRAY,
            font=("Malgun Gothic", 8), width=8, anchor="w"
        ).pack(side="left")

        tk.Label(
            row, text=message, bg=WHITE, fg=color,
            font=("Malgun Gothic", 9), anchor="w",
            justify="left", wraplength=300
        ).pack(side="left", fill="x", expand=True)

        canvas.update_idletasks()
        canvas.yview_moveto(1.0)

    app.notify = add_notice
    add_notice("프로그램이 실행되었습니다.")
