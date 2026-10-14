import tkinter as tk
from tkinter import ttk
from config import WHITE, BORDER, TEXT, BLUE, BLUE_LIGHT

# ==========================================
# 테마 스타일을 설정하는 함수
# ==========================================
def configure_style():
    style = ttk.Style()
    style.theme_use("clam")

    # TEntry 위젯의 배경색, 테두리, 패딩, 폰트 등 공통 디자인 스타일 설정
    style.configure(
        "TEntry",
        fieldbackground=WHITE,
        background=WHITE,
        bordercolor=BORDER,
        lightcolor=BORDER,
        darkcolor=BORDER,
        padding=7,
        font=("Malgun Gothic", 10)
    )

# ==========================================
# UI 모듈별 공통 컨테이너를 생성하는 함수
# ==========================================
def create_panel(parent, title, header_button_text=None, header_button_command=None):
    panel = tk.Frame(
        parent,
        bg=WHITE,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    # 컨테이너 내부 헤더 영역 생성
    header = tk.Frame(panel, bg=WHITE)
    header.pack(fill="x", padx=18, pady=(12, 8))

    # 타이틀 생성
    tk.Label(
        header,
        text=title,
        bg=WHITE,
        fg=TEXT,
        font=("Malgun Gothic", 13, "bold")
    ).pack(side="left")

    # 헤더 우측에 버튼이 필요한 경우 버튼 생성 및 배치
    if header_button_text:
        create_outline_button(
            header,
            header_button_text,
            header_button_command
        ).pack(side="right")

    # 헤더와 본문 영역을 시각적으로 구분하는 가로 구분선 생성
    tk.Frame(
        panel,
        bg=BORDER,
        height=1
    ).pack(fill="x", padx=18)

    return panel

# ==========================================
# 일관된 스타일의 버튼을 생성하는 공통 함수
# ==========================================
def create_outline_button(parent, text, command=None):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=WHITE,
        fg=BLUE,
        activebackground=BLUE_LIGHT,
        activeforeground=BLUE,
        relief="solid",
        bd=1,
        highlightthickness=0,
        font=("Malgun Gothic", 9, "bold"),
        padx=11,
        pady=6,
        cursor="hand2"
    )

# ==========================================
# 라벨, 입력창, 선택적 버튼이 포함된 입력 필드 행을 생성하는 함수
# ==========================================
def create_field(parent, label, variable, button_text=None, command=None):
    row = tk.Frame(parent, bg=WHITE)
    row.pack(fill="x", padx=20, pady=5)

    # 항목 이름 생성
    tk.Label(
        row,
        text=label,
        width=15,
        anchor="w",
        bg=WHITE,
        fg=TEXT,
        font=("Malgun Gothic", 9)
    ).pack(side="left")

    # 텍스트 입력용 ttk.Entry 생성
    entry = ttk.Entry(row, textvariable=variable)
    entry.pack(side="left", fill="x", expand=True)

    # 우측에 버튼이 필요한 경우 버튼 생성 및 배치
    if button_text:
        create_outline_button(row, button_text, command).pack(side="left", padx=(8, 0))

    return entry