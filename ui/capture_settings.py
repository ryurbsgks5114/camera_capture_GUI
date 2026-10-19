import tkinter as tk
from tkinter import ttk
from config import WHITE, TEXT, BLUE
from ui.common import create_panel

# ==========================================
# 촬영 설정 UI 및 기능 함수
# ==========================================
def build(parent, app):
    # 상위 패널 생성
    panel = create_panel(parent, "촬영 설정")
    panel.pack(fill="x", pady=(0, 5))

    # 촬영 시작 시간 설정 영역
    time_row = tk.Frame(panel, bg=WHITE)
    time_row.pack(fill="x", padx=20, pady=5)

    tk.Label(
        time_row,
        text="촬영 시작 시간",
        width=15,
        anchor="w",
        bg=WHITE,
        fg=TEXT,
        font=("Malgun Gothic", 9)
    ).pack(side="left")

    hour_entry = ttk.Entry(
        time_row,
        textvariable=app.state.hour_var,
        width=3,
        justify="center",
        validate="key",
        validatecommand=app.vcmd
    )
    hour_entry.pack(side="left")

    tk.Label(
        time_row,
        text=" : ",
        bg=WHITE,
        fg=TEXT,
        font=("Malgun Gothic", 10, "bold")
    ).pack(side="left")

    minute_entry = ttk.Entry(
        time_row,
        textvariable=app.state.minute_var,
        width=3,
        justify="center",
        validate="key",
        validatecommand=app.vcmd
    )
    minute_entry.pack(side="left")

    tk.Label(
        time_row,
        text=" : ",
        bg=WHITE,
        fg=TEXT,
        font=("Malgun Gothic", 10, "bold")
    ).pack(side="left")

    second_entry = ttk.Entry(
        time_row,
        textvariable=app.state.second_var,
        width=3,
        justify="center",
        validate="key",
        validatecommand=app.vcmd
    )
    second_entry.pack(side="left")

    # 촬영 시작 시간 관련 안내 문구 생성
    tk.Label(
        panel,
        text="※ 현재 시간이 설정 시간을 이미 지났다면 즉시 촬영이 시작됩니다.",
        bg=WHITE,
        fg=BLUE,
        justify="left",
        font=("Malgun Gothic", 8)
    ).pack(fill="x", padx=20, pady=(0, 8))

    # 촬영 간격 설정 영역
    interval_row = tk.Frame(panel, bg=WHITE)
    interval_row.pack(fill="x", padx=20, pady=5)

    tk.Label(
        interval_row,
        text="촬영 간격",
        width=15,
        anchor="w",
        bg=WHITE,
        fg=TEXT,
        font=("Malgun Gothic", 9)
    ).pack(side="left")

    interval_entry = ttk.Entry(
        interval_row,
        textvariable=app.state.interval_var,
        width=12,
        justify="right",
        validate="key",
        validatecommand=app.vcmd
    )
    interval_entry.pack(side="left")

    tk.Label(
        interval_row,
        text=" 분",
        bg=WHITE,
        fg=TEXT,
        font=("Malgun Gothic", 10)
    ).pack(side="left")

    # ==========================================
    # 입력값이 변경될 때마다 실시간으로 랜더링하는 함수
    # ==========================================
    def update(*args):
        app.state.start_time_display.set(
            app.state.hour_var.get() + ":" +
            app.state.minute_var.get() + ":" +
            app.state.second_var.get()
        )
        app.state.interval_display.set(app.state.interval_var.get() + " 분")

    # 각 입력 변수에 값 변경 감지 이벤트 바인딩
    app.state.hour_var.trace_add("write", update)
    app.state.minute_var.trace_add("write", update)
    app.state.second_var.trace_add("write", update)
    app.state.interval_var.trace_add("write", update)

    # ==========================================
    # 촬영 설정 입력란 잠금 및 해제 함수
    # ==========================================
    def set_capture_settings_locked(locked):
        # 잠김 상태(locked)에 따라 입력창 상태를 비활성화(disabled) 또는 활성화(normal)로 설정
        new_state = "disabled" if locked else "normal"

        # 시, 분, 초, 촬영 간격 입력창들의 상태 일괄 변경
        hour_entry.configure(state=new_state)
        minute_entry.configure(state=new_state)
        second_entry.configure(state=new_state)
        interval_entry.configure(state=new_state)

    # 촬영 제어 화면의 일괄 잠금 관리 목록에 등록
    app.capture_settings_lockers.append(
        set_capture_settings_locked
    )