import tkinter as tk
from config import (
    WHITE,
    FTP_HOST,
    FTP_PORT,
    FTP_USER,
    FTP_PASSWORD
)
from ui.common import create_panel, create_field, create_outline_button

# ==========================================
# FTP 설정 UI 및 기능 함수
# ==========================================
def build(parent, app):
    # '기본값 불러오기' 버튼 클릭 시 호출되는 함수
    def default_load():
        # config에 정의된 기본 FTP 설정값들을 입력 필드에 세팅
        app.state.ftp_host.set(FTP_HOST)
        app.state.ftp_port.set(str(FTP_PORT))
        app.state.ftp_user.set(FTP_USER)
        app.state.ftp_password.set(FTP_PASSWORD)

        app.notify("FTP 기본값을 불러왔습니다.")

    # '연결 테스트' 버튼 클릭 시 호출되는 함수
    def connection_test():
        app.state.ftp_status.set("연결됨")
        app.refresh_system_status()
        app.notify("FTP 연결 테스트가 완료되었습니다.")

    # 상위 패널 생성 및 '연결 테스트' 버튼 연결
    panel = create_panel(parent, "FTP 설정", "🔗  연결 테스트", connection_test)
    panel.pack(fill="x", pady=5)

    # FTP 설정 입력 필드 생성
    create_field(panel, "FTP Host", app.state.ftp_host)
    create_field(panel, "FTP Port", app.state.ftp_port)
    create_field(panel, "FTP User", app.state.ftp_user)
    create_field(panel, "FTP Password", app.state.ftp_password)

    # '기본값 불러오기' 버튼 담을 프레임 생성
    button_area = tk.Frame(panel, bg=WHITE)
    button_area.pack(fill="x", padx=20, pady=12)

    # '기본값 불러오기' 아웃라인 버튼 생성 및 우측 정렬 배치
    create_outline_button(button_area, "⬇  기본값 불러오기", default_load).pack(side="right")