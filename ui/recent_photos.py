import tkinter as tk
from pathlib import Path
from PIL import Image, ImageTk
from config import SUBTEXT
from ui.common import create_panel

# 기본 사진 이미지 경로
PLACEHOLDER_PATH = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "no_image.png"
)

# ==========================================
# 사진 미리보기 카드 생성 함수
# ==========================================
def build_photo_preview(parent, view_name):
    # 개별 사진 카드 프레임 생성
    card = tk.Frame(
        parent,
        bg="#FFFFFF",
        highlightbackground="#D8E2EF",
        highlightthickness=1,
        width=300,
        height=330
    )
    card.pack(side="left", fill="y", expand=True, padx=5, pady=6)

    # 카드 크기가 내부 위젯에 의해 임의로 변경되지 않도록 설정
    card.pack_propagate(False)

    # 뷰 이름(사이드 뷰 / 탑 뷰) 표시 레이블
    tk.Label(
        card,
        text=view_name,
        bg="#FFFFFF",
        fg="#183B63",
        font=("Malgun Gothic", 10, "bold"),
        anchor="w"
    ).pack(
        fill="x",
        padx=10,
        pady=(8, 6)
    )

    # 정사각형 사진 표시 영역 프레임
    photo_area = tk.Frame(
        card,
        bg="#F7FAFF",
        highlightbackground="#CFDBEB",
        highlightthickness=1,
        width=250,
        height=250
    )
    photo_area.pack(anchor="center", padx=5, pady=(0, 6))

    # 사진 영역의 가로, 세로 크기를 유지
    photo_area.pack_propagate(False)

    # 사진이 없을 때 표시할 기본 이미지
    placeholder_image = Image.open(PLACEHOLDER_PATH).convert("RGBA")
    # 이미지 크기를 64x64 픽셀로 조절
    placeholder_image = placeholder_image.resize((64, 64))
    # Tkinter에서 사용할 수 있는 이미지 객체로 변환
    placeholder_photo = ImageTk.PhotoImage(placeholder_image)
    
    # 기본 이미지 표시
    placeholder_label = tk.Label(photo_area, image=placeholder_photo, bg="#F7FAFF")
    placeholder_label.pack(expand=True, pady=(12, 0))
    
    # 이미지가 메모리에서 사라지지 않도록 참조 유지
    placeholder_label.image = placeholder_photo

    # 사진 파일명을 표시할 레이블
    filename_label = tk.Label(
        card,
        text="파일명: ",
        bg="#FFFFFF",
        fg=SUBTEXT,
        font=("Malgun Gothic", 8),
        anchor="w"
    )
    filename_label.pack(fill="x", padx=8, pady=(0, 6))

    return card

# ==========================================
# 최근 촬영 사진 패널 UI 생성 함수
# ==========================================
def build(parent, app):
    # 상위 패널 생성
    panel = create_panel(parent, "최근 촬영 사진")
    panel.pack(fill="both", expand=False, pady=(0, 10))

    # 사이드 뷰와 탑 뷰를 가로로 배치할 컨테이너 프레임
    photo_container = tk.Frame(panel, bg="#FFFFFF")
    photo_container.pack(fill="x", expand=False, padx=8, pady=6)

    # 사이드 뷰 및 탑 뷰 썸네일 카드 생성 함수 호출
    build_photo_preview(photo_container, "사이드 뷰")
    build_photo_preview(photo_container, "탑 뷰")