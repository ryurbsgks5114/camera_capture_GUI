import tkinter as tk
from tkinter import filedialog, simpledialog

from ui.common import create_panel, create_field


def build(parent, app):
    def change_local_path():
        selected = filedialog.askdirectory(title="로컬 저장 폴더 선택")
        if selected:
            app.state.local_path.set(selected)
            app.notify("로컬 저장 경로가 변경되었습니다.")

    def change_ftp_path():
        selected = simpledialog.askstring(
            "FTP 저장 경로 선택",
            "FTP 저장 경로를 입력하세요.",
            initialvalue=app.state.ftp_path.get()
        )
        if selected:
            app.state.ftp_path.set(selected)
            app.notify("FTP 저장 경로가 변경되었습니다.")

    panel = create_panel(parent, "저장 경로 설정")
    panel.pack(fill="x", pady=5)

    local_entry = create_field(
        panel, "로컬 저장 경로", app.state.local_path,
        "📁 선택", change_local_path
    )
    local_entry.configure(state="readonly")

    ftp_entry = create_field(
        panel, "FTP 저장 경로", app.state.ftp_path,
        "📁 선택", change_ftp_path
    )
    ftp_entry.configure(state="readonly")
