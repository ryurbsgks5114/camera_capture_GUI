import tkinter as tk

from config import WHITE, BORDER, TEXT, GREEN, GRAY, GRAY_LIGHT, RED, BLUE
from ui.common import create_panel


def build(parent, app):
    panel = create_panel(parent, "촬영 제어")
    panel.pack(fill="both", expand=True, pady=5)

    body = tk.Frame(panel, bg=WHITE)
    body.pack(fill="both", expand=True, padx=18, pady=14)
    app.control_body = body

    def create_capture_state(title, status_color, card_bg, button_text, button_bg, show_details):
        card = tk.Frame(body, bg=card_bg, highlightbackground=BORDER, highlightthickness=1)

        tk.Label(card, text="●", bg=card_bg, fg=status_color,
                 font=("Arial", 25)).pack(pady=(16, 0))
        tk.Label(card, text=title, bg=card_bg, fg=status_color,
                 font=("Malgun Gothic", 14, "bold")).pack(pady=4)

        if show_details:
            tk.Label(card, text="촬영 시작 시간", bg=card_bg, fg=TEXT,
                     font=("Malgun Gothic", 8)).pack(pady=(10, 0))
            tk.Label(card, textvariable=app.state.start_time_display,
                     bg=card_bg, fg=TEXT,
                     font=("Malgun Gothic", 10, "bold")).pack()
            tk.Label(card, text="촬영 간격", bg=card_bg, fg=TEXT,
                     font=("Malgun Gothic", 8)).pack(pady=(5, 0))
            tk.Label(card, textvariable=app.state.interval_display,
                     bg=card_bg, fg=TEXT,
                     font=("Malgun Gothic", 10, "bold")).pack()

        button = tk.Button(
            card, text=button_text, bg=button_bg, fg=WHITE,
            activebackground=button_bg, activeforeground=WHITE,
            relief="flat", bd=0, font=("Malgun Gothic", 11, "bold"),
            padx=15, pady=10
        )
        button.pack(fill="x", padx=16, pady=(12, 16))
        return card, button

    idle_card, idle_button = create_capture_state(
        "대기 중", GRAY, GRAY_LIGHT, "▶  촬영 시작", BLUE, False
    )
    idle_card.pack(fill="both", expand=True)

    running_card, running_button = create_capture_state(
        "촬영 중", GREEN, "#EDF9F2", "■  촬영 중지", RED, True
    )
    running_card.pack_forget()

    def show_running():
        idle_card.pack_forget()
        running_card.pack(fill="both", expand=True)
        app.state.capture_status.set("촬영 중")
        app.refresh_system_status()
        app.notify("촬영이 진행 중입니다.")

    def show_idle():
        running_card.pack_forget()
        idle_card.pack(fill="both", expand=True)
        app.state.capture_status.set("대기 중")
        app.refresh_system_status()
        app.notify("촬영이 대기 상태입니다.")

    idle_button.configure(command=show_running)
    running_button.configure(command=show_idle)
