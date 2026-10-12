import tkinter as tk

from config import BG, WHITE, TEXT, SUBTEXT


def build_header(root):
    header = tk.Frame(root, bg=WHITE, height=70)
    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(
        header, text="📷  Camera Manager", bg=WHITE, fg=TEXT,
        font=("Malgun Gothic", 18, "bold")
    ).pack(side="left", padx=24)

    tk.Label(
        header, text="2026-10-08 (목) 13:14:00",
        bg=WHITE, fg=SUBTEXT, font=("Malgun Gothic", 9)
    ).pack(side="right", padx=24)


def build_main(root):
    main = tk.Frame(root, bg=BG)
    main.pack(fill="both", expand=True, padx=14, pady=14)

    main.grid_columnconfigure(0, weight=30)
    main.grid_columnconfigure(1, weight=36)
    main.grid_columnconfigure(2, weight=34)
    main.grid_rowconfigure(0, weight=1)

    left = tk.Frame(main, bg=BG)
    left.grid(row=0, column=0, sticky="nsew", padx=(0, 7))

    center = tk.Frame(main, bg=BG)
    center.grid(row=0, column=1, sticky="nsew", padx=7)

    right = tk.Frame(main, bg=BG)
    right.grid(row=0, column=2, sticky="nsew", padx=(7, 0))

    return main, left, center, right
