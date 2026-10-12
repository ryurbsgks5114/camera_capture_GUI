import tkinter as tk

from config import WHITE, BLUE, BLUE_LIGHT
from ui.common import create_panel


def build(parent, app):
    def connection_test():
        app.state.server_status.set("연결됨")
        app.refresh_system_status()
        app.notify("라즈베리파이 서버 연결 테스트가 완료되었습니다.")

    panel = create_panel(parent, "서버 연결", "🔗  연결 테스트", connection_test)
    panel.pack(fill="x", pady=5)

    body = tk.Frame(panel, bg=WHITE)
    body.pack(fill="x", padx=20, pady=12)

    tk.Label(
        body,
        text=(
            "ⓘ  설정된 IP 주소와 포트로 자동 연결됩니다.\n"
            "    사용자가 직접 수정할 수 없습니다."
        ),
        bg=BLUE_LIGHT,
        fg=BLUE,
        justify="left",
        font=("Malgun Gothic", 8),
        padx=10,
        pady=9
    ).pack(fill="x")
