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

    # options 목록을 순회하며 라디오 버튼 생성 및 배치
    for value, label in options:
        tk.Radiobutton(
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
        ).pack(fill="x", padx=24, pady=5)