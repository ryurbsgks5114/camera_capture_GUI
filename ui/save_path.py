import posixpath
import threading
import tkinter as tk
from tkinter import filedialog, ttk
from config import WHITE, RED, TEXT, SUBTEXT, BORDER, BLUE
from services.ftp_client import list_ftp_directories
from services.ftp_validator import validate_ftp_settings
from ui.common import create_panel, create_field
from ui.ftp_browser import open_ftp_browser

# ==========================================
# 저장 경로 설정 UI 및 기능 함수
# ==========================================
def build(parent, app):
    # '로컬 저장 경로'의 '선택' 버튼 클릭 시 호출되는 함수
    def change_local_path():
        selected = filedialog.askdirectory(title="로컬 저장 폴더 선택")

        if selected:
            app.state.local_path.set(selected)
            app.notify("로컬 저장 경로가 변경되었습니다.")

    # 'FTP 저장 경로'의 '선택' 버튼 클릭 시 호출되는 함수
    def change_ftp_path():
        # 입력된 FTP 설정값 가져오기
        host = app.state.ftp_host.get().strip()
        port_text = app.state.ftp_port.get().strip()
        user = app.state.ftp_user.get().strip()
        password = app.state.ftp_password.get()

        # FTP 설정값 검증
        valid, message, port = validate_ftp_settings(
            host=host,
            port_text=port_text,
            user=user,
            password=password
        )

        if not valid:
            app.notify(message, RED)
            return

        # 검증 완료 후 FTP 폴더 브라우저 창 오픈
        open_ftp_browser(app, host, port, user, password)

    # 상위 패널 생성
    panel = create_panel(parent, "저장 경로 설정")
    panel.pack(fill="x", pady=5)

    # 로컬 저장 경로 필드 생성 및 읽기 전용 설정
    local_entry = create_field(
        panel,
        "로컬 저장 경로",
        app.state.local_path,
        "📁 선택",
        change_local_path
    )
    local_entry.configure(state="readonly")

    # FTP 저장 경로 필드 생성 및 읽기 전용 설정
    ftp_entry = create_field(
        panel,
        "FTP 저장 경로",
        app.state.ftp_path,
        "📁 선택",
        change_ftp_path
    )
    ftp_entry.configure(state="readonly")

    # 저장 경로 선택 버튼 잠금 및 해제 함수
    def set_save_path_locked(locked):
        # 잠김 상태(locked)에 따라 버튼 상태를 비활성화(disabled) 또는 활성화(normal)로 설정
        new_state = "disabled" if locked else "normal"

        # 로컬 저장 경로 및 FTP 저장 경로 설정 버튼들의 상태 일괄 변경
        local_entry.action_button.configure(state=new_state)
        ftp_entry.action_button.configure(state=new_state)

    # 촬영 제어 화면의 일괄 잠금 관리 목록에 등록
    app.capture_settings_lockers.append(
        set_save_path_locked
    )