import tkinter as tk
from tkinter import ttk

from config import WHITE, BORDER, TEXT, BLUE, BLUE_LIGHT


def configure_style():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "TEntry",
        fieldbackground=WHITE,
        background=WHITE,
        bordercolor=BORDER,
        lightcolor=BORDER,
        darkcolor=BORDER,
        padding=7,
        font=("Malgun Gothic", 10)
    )


def create_panel(parent, title, header_button_text=None, header_button_command=None):
    panel = tk.Frame(
        parent,
        bg=WHITE,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    header = tk.Frame(panel, bg=WHITE)
    header.pack(fill="x", padx=18, pady=(12, 8))

    tk.Label(
        header,
        text=title,
        bg=WHITE,
        fg=TEXT,
        font=("Malgun Gothic", 13, "bold")
    ).pack(side="left")

    if header_button_text:
        create_outline_button(
            header,
            header_button_text,
            header_button_command
        ).pack(side="right")

    tk.Frame(
        panel,
        bg=BORDER,
        height=1
    ).pack(fill="x", padx=18)

    return panel


def create_outline_button(parent, text, command=None):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=WHITE,
        fg=BLUE,
        activebackground=BLUE_LIGHT,
        activeforeground=BLUE,
        relief="solid",
        bd=1,
        highlightthickness=0,
        font=("Malgun Gothic", 9, "bold"),
        padx=11,
        pady=6,
        cursor="hand2"
    )


def create_field(parent, label, variable, button_text=None, command=None):
    row = tk.Frame(parent, bg=WHITE)
    row.pack(fill="x", padx=20, pady=5)

    tk.Label(
        row,
        text=label,
        width=15,
        anchor="w",
        bg=WHITE,
        fg=TEXT,
        font=("Malgun Gothic", 9)
    ).pack(side="left")

    entry = ttk.Entry(row, textvariable=variable)
    entry.pack(side="left", fill="x", expand=True)

    if button_text:
        create_outline_button(row, button_text, command).pack(
            side="left",
            padx=(8, 0)
        )

    return entry
