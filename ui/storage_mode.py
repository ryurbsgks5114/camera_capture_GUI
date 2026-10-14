import tkinter as tk
from config import WHITE, TEXT
from ui.common import create_panel

# ==========================================
# 저장 방식 설정 UI 및 기능 함수
# ==========================================
def build(parent, app):
    # '저장' 버튼 클릭 시 호출되는 함수
    def save():
        # 저장 방식 - 텍스트 맵핑
        mode_text = {
            "both": "로컬 + FTP 저장",
            "local": "로컬 저장",
            "ftp": "FTP 저장"
        }

        # 선택된 저장 방식을 알림으로 띄우기
        app.notify(
            "저장 방식이 '" +
            mode_text.get(app.state.storage_mode.get(), "") +
            "'으로 설정되었습니다."
        )

    # 상위 패널 생성 및 '저장' 버튼 연결
    panel = create_panel(parent, "저장 방식", "저장", save)
    panel.pack(fill="x", pady=5)

    # 선택 가능한 저장 방식 옵션 목록
    options = [
        ("both", "로컬 + FTP 저장"),
        ("local", "로컬 저장"),
        ("ftp", "FTP 저장")
    ]

    # 라디오 버튼들을 보관할 리스트 초기화
    storage_radio_buttons = []

    # options 목록을 순회하며 라디오 버튼 생성 및 배치
    for value, label in options:
        radio_button = tk.Radiobutton(
            panel,
            text=label,
            variable=app.state.storage_mode,
            value=value,
            bg=WHITE,
            fg=TEXT,
            activebackground=WHITE,
            selectcolor=WHITE,
            font=("Malgun Gothic", 10),
            anchor="w"
        )
        radio_button.pack(fill="x", padx=24, pady=5)

        # 생성된 라디오 버튼을 관리 목록에 추가
        storage_radio_buttons.append(radio_button)

    # 촬영 중 저장 방식 선택 잠금 및 해제 함수
    def set_storage_mode_locked(locked):
        # 잠김 상태(locked)에 따라 라디오 버튼 상태를 비활성화(disabled) 또는 활성화(normal)로 설정
        new_state = "disabled" if locked else "normal"

        # 보관된 모든 라디오 버튼에 일괄적으로 상태 적용
        for radio_button in storage_radio_buttons:
            radio_button.configure(state=new_state)

    # 촬영 제어 화면의 일괄 잠금 관리 목록에 등록
    app.capture_settings_lockers.append(
        set_storage_mode_locked
    )