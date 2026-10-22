import tkinter as tk
from config import WHITE, TEXT, GREEN, GRAY, RED
from ui.common import create_panel

# ==========================================
# 상태에 따라 해당하는 색상 코드를 반환하는 함수
# ==========================================
def get_status_color(status):
    if status in ("연결됨", "촬영 중"):
        return GREEN
    if status == "연결 실패":
        return RED

    return GRAY

# ==========================================
# 시스템 상태 UI를 생성하는 함수
# ==========================================
def build(parent, app):
    # 상위 패널 생성
    panel = create_panel(parent, "시스템 상태")
    panel.pack(fill="x", pady=(0, 10))

    # 상태 항목들이 렌더링될 내부 프레임 생성
    app.system_body = tk.Frame(panel, bg=WHITE)
    app.system_body.pack(fill="x", padx=20, pady=8)

    # 최초 패널 생성 시 상태 목록 렌더링 수행
    refresh(app)

    return panel

# ==========================================
# 시스템 상태 정보를 최신 값으로 갱신하여 다시 렌더링 하는 함수
# ==========================================
def refresh(app):
    # 기존에 그려져 있던 하위 위젯들을 모두 초기화
    for widget in app.system_body.winfo_children():
        widget.destroy()

    # 표시할 시스템 상태 항목과 현재 상태값 매핑 목록
    statuses = [
        ("서버 연결 상태", app.state.server_status.get()),
        ("WebSocket 상태", app.state.websocket_status.get()),
        ("촬영 상태", app.state.capture_status.get()),
        ("FTP 연결 상태", app.state.ftp_status.get())
    ]

    # 상태 항목별로 행 프레임, 상태 표시용 원, 텍스트 라벨 생성 및 배치
    for label, value in statuses:
        row = tk.Frame(app.system_body, bg=WHITE)
        row.pack(fill="x", pady=8)

        # 항목 이름 생성
        tk.Label(
            row,
            text=label,
            width=15,
            anchor="w",
            bg=WHITE,
            fg=TEXT,
            font=("Malgun Gothic", 10)
        ).pack(side="left")

        # 상태에 따른 색상 코드 가져오기
        color = get_status_color(value)

        # 신호등 형태의 상태 표시용 원 생성
        canvas = tk.Canvas(row, width=15, height=15, bg=WHITE, highlightthickness=0)
        canvas.pack(side="left", padx=(0, 7))
        canvas.create_oval(3, 3, 12, 12, fill=color, outline=color)

        # 상태 텍스트 생성
        tk.Label(
            row,
            text=value,
            bg=WHITE,
            fg=color,
            font=("Malgun Gothic", 10, "bold")
        ).pack(side="left")