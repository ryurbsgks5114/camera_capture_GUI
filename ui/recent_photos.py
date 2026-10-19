import tkinter as tk

from config import BG, SUBTEXT
from ui.common import create_panel

# ==========================================
# 최근 촬영 사진 패널 UI 생성 함수
# ==========================================
def build(parent, app):
    # 상위 패널 생성
    panel = create_panel(parent, "최근 촬영 사진")
    panel.pack(fill="both", expand=True, pady=(0, 10))

    # 사진이 표시될 내부 영역 생성
    area = tk.Frame(
        panel, bg="#F7FAFF",
        highlightbackground="#CFDBEB", highlightthickness=1
    )
    area.pack(fill="both", expand=True, padx=18, pady=18)

    # 영역 중앙에 배치할 아이콘 라벨 생성
    tk.Label(
        area, text="▧", bg="#F7FAFF", fg="#B0BFD1",
        font=("Arial", 42)
    ).pack(expand=True, pady=(30, 0))

    # 안내 문구 라벨 생성
    tk.Label(
        area,
        text=("최근 촬영된 사진이 여기에 표시됩니다.\n"
              "(추후 기능 확정 예정)"),
        bg="#F7FAFF", fg=SUBTEXT,
        font=("Malgun Gothic", 9), justify="center"
    ).pack(expand=True, pady=(0, 30))