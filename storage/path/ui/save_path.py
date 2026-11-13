
from tkinter import filedialog

from config import (WHITE, RED, FTP_HOST, FTP_PORT, FTP_USER, FTP_PASSWORD)

from common.ui.common import create_panel, create_field
from storage.path.ui.ftp_browser import open_ftp_browser

from storage.path.service.path_settings_storage import save_path_settings


def build(parent, app):
    """저장 경로 설정 UI를 생성합니다.

    Args:
        parent (tk.Widget): 저장 경로 UI를 배치할 부모 위젯
        app (CameraManagerApp): 애플리케이션 인스턴스

    Returns:
        tuple: 저장 경로 패널과 입력 잠금 콜백
    """

    def change_local_path():
        """로컬 저장 폴더를 선택하고 변경된 경로를 저장합니다."""
        selected = filedialog.askdirectory(title="로컬 저장 폴더 선택")

        if not selected:
            return

        app.state.local_path.set(selected)

        if save_path_settings(app.state.local_path.get(), app.state.ftp_path.get()):
            app.notify("로컬 저장 경로가 변경되었습니다.")
        else:
            app.notify("경로는 변경되었지만 설정 파일 저장에 실패했습니다.", RED)

    def change_ftp_path():
        """FTP 폴더 선택 창을 실행합니다."""
        open_ftp_browser(app, FTP_HOST, FTP_PORT, FTP_USER, FTP_PASSWORD)

    panel = create_panel(parent, "저장 경로 설정")
    panel.pack(fill="x", pady=5)

    local_entry = create_field(
        panel,
        "로컬 저장 경로",
        app.state.local_path,
        "📁 선택",
        change_local_path,
    )
    local_entry.configure(state="readonly")

    ftp_entry = create_field(
        panel,
        "FTP 저장 경로",
        app.state.ftp_path,
        "📁 선택",
        change_ftp_path,
    )
    ftp_entry.configure(state="readonly")

    def set_save_path_locked(locked):
        """촬영 상태에 따라 저장 경로 선택 버튼을 잠그거나 해제합니다.

        Args:
            locked (bool): True이면 버튼을 비활성화합니다.
        """
        new_state = "disabled" if locked else "normal"

        local_entry.action_button.configure(state=new_state)
        ftp_entry.action_button.configure(state=new_state)

    return panel, set_save_path_locked
