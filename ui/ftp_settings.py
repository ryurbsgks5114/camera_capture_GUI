import tkinter as tk

from config import WHITE
from ui.common import create_panel, create_field, create_outline_button


def build(parent, app):
    def default_load():
        app.state.ftp_host.set("기본값")
        app.state.ftp_port.set("기본값")
        app.state.ftp_user.set("기본값")
        app.state.ftp_password.set("********")
        app.notify("FTP 기본값을 불러왔습니다.")

    def connection_test():
        app.state.ftp_status.set("연결됨")
        app.refresh_system_status()
        app.notify("FTP 연결 테스트가 완료되었습니다.")

    panel = create_panel(parent, "FTP 설정", "🔗  연결 테스트", connection_test)
    panel.pack(fill="x", pady=5)

    create_field(panel, "FTP Host", app.state.ftp_host)
    create_field(panel, "FTP Port", app.state.ftp_port)
    create_field(panel, "FTP User", app.state.ftp_user)
    create_field(panel, "FTP Password", app.state.ftp_password)

    button_area = tk.Frame(panel, bg=WHITE)
    button_area.pack(fill="x", padx=20, pady=12)

    create_outline_button(
        button_area, "⬇  기본값 불러오기", default_load
    ).pack(side="right")
