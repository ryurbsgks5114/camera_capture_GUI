
from tkinter import filedialog
from config import (WHITE, RED, FTP_HOST, FTP_PORT, FTP_USER, FTP_PASSWORD)
from ui.common import create_panel, create_field
from ui.ftp_browser import open_ftp_browser


# ==========================================
# 저장 경로 설정 UI 및 기능 함수
# ==========================================
def build(parent, app):

    # ==========================================
    # '로컬 저장 경로'의 '선택' 버튼 클릭 시 호출되는 함수
    # ==========================================
    def change_local_path():
        selected = filedialog.askdirectory(title="로컬 저장 폴더 선택")

        if selected:
            app.state.local_path.set(selected)

            if app.state.save_path_settings():
                app.notify("로컬 저장 경로가 변경되었습니다.")
            else:
                app.notify(
                    "경로는 변경되었지만 설정 파일 저장에 실패했습니다.",
                    RED
                )

    # ==========================================
    # 'FTP 저장 경로'의 '선택' 버튼 클릭 시 호출되는 함수
    # ==========================================
    def change_ftp_path():

        # GUI config.py에 정의된 FTP 접속정보로 폴더 브라우저 실행
        open_ftp_browser(
            app,
            FTP_HOST,
            FTP_PORT,
            FTP_USER,
            FTP_PASSWORD
        )

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

    # ==========================================
    # 저장 경로 선택 버튼 잠금 및 해제 함수
    # ==========================================
    def set_save_path_locked(locked):
        # 잠김 상태(locked)에 따라 버튼 상태를 비활성화 또는 활성화
        new_state = "disabled" if locked else "normal"

        # 로컬 저장 경로 및 FTP 저장 경로 설정 버튼 상태 변경
        local_entry.action_button.configure(state=new_state)
        ftp_entry.action_button.configure(state=new_state)

    # 촬영 제어 화면의 일괄 잠금 관리 목록에 등록
    app.capture_settings_lockers.append(
        set_save_path_locked
    )
