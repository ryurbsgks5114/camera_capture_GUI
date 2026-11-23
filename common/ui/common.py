
import tkinter as tk

from tkinter import ttk

from config import WHITE, BORDER, TEXT, BLUE, BLUE_LIGHT


def configure_style():
    """애플리케이션에서 사용하는 Tkinter 공통 테마 스타일을 설정합니다."""
    style = ttk.Style()
    style.theme_use("clam")

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


def create_panel(parent, title, header_button_text=None, header_button_command=None):
    """공통 디자인이 적용된 UI 패널을 생성합니다.

    Args:
        parent (tk.Widget): 패널을 배치할 부모 위젯
        title (str): 패널 헤더에 표시할 제목
        header_button_text (str, optional): 헤더 우측 버튼에 표시할 문구
        header_button_command (callable, optional): 헤더 버튼 실행 함수

    Returns:
        tk.Frame: 생성된 패널 위젯
    """
    panel = tk.Frame(
        parent,
        bg=WHITE,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    header = tk.Frame(panel, bg=WHITE)
    header.pack(fill="x", padx=12, pady=(7, 4))

    tk.Label(
        header,
        text=title,
        bg=WHITE,
        fg=TEXT,
        font=("Malgun Gothic", 13, "bold")
    ).pack(side="left")

    panel.header_button = None

    if header_button_text:
        panel.header_button = create_outline_button(
            header,
            header_button_text,
            header_button_command
        )
        panel.header_button.pack(side="right")

    tk.Frame(
        panel,
        bg=BORDER,
        height=1
    ).pack(fill="x", padx=12)

    return panel


def create_outline_button(parent, text, command=None):
    """공통 테두리 버튼 위젯을 생성합니다.

    Args:
        parent (tk.Widget): 버튼을 배치할 부모 위젯
        text (str): 버튼에 표시할 문구
        command (callable, optional): 버튼 클릭 시 실행할 함수

    Returns:
        tk.Button: 생성된 버튼 위젯
    """
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


def create_field(parent, label, variable, button_text=None, command=None):
    """라벨, 입력창 및 선택적 버튼으로 구성된 입력 필드 행을 생성합니다.

    Args:
        parent (tk.Widget): 입력 필드 행을 배치할 부모 위젯
        label (str): 입력 항목에 표시할 라벨
        variable (tk.Variable): 입력창과 연결할 Tkinter 변수
        button_text (str, optional): 우측 버튼에 표시할 문구
        command (callable, optional): 우측 버튼 실행 함수

    Returns:
        ttk.Entry: 생성된 입력창 위젯
    """
    row = tk.Frame(parent, bg=WHITE)
    row.pack(fill="x", padx=20, pady=5)

    tk.Label(
        row,
        text=label,
        width=15,
        anchor="w",
        bg=WHITE,
        fg=TEXT,
        font=("Malgun Gothic", 9)
    ).pack(side="left")

    entry = ttk.Entry(row, textvariable=variable)
    entry.pack(side="left", fill="x", expand=True)

    if button_text:
        action_button = create_outline_button(row, button_text, command)
        action_button.pack(side="left", padx=(8, 0))

        entry.action_button = action_button

    return entry
