
import tkinter as tk

from config import WHITE, BORDER, GREEN, GRAY, GRAY_LIGHT, RED, BLUE

from common.ui.common import create_panel

from capture.control.service.capture_control_service import CaptureControlService


def build(parent, app, before_start_capture=None):
    """촬영 제어 UI를 생성하고 촬영 제어 Service를 연결합니다.

    Args:
        parent (tk.Widget): 촬영 제어 UI를 배치할 부모 위젯
        app (CameraManagerApp): 애플리케이션 인스턴스
        before_start_capture (Callable, optional): 촬영 시작 전 실행할 작업

    Returns:
        tk.Frame: 생성된 촬영 제어 패널
    """
    panel = create_panel(parent, "촬영 제어")
    panel.configure(height=120)
    panel.pack(fill="both", expand=False, pady=5)
    panel.pack_propagate(False)

    body = tk.Frame(panel, bg=WHITE)
    body.pack(fill="both", expand=True, padx=18, pady=9)
    app.control_body = body

    def create_capture_state(title, status_color, card_bg, button_text, button_bg):
        """촬영 상태 카드와 버튼을 생성합니다.

        Args:
            title (str): 상태 표시 문구
            status_color (str): 상태 표시 색상
            card_bg (str): 카드 배경색
            button_text (str): 버튼 표시 문구
            button_bg (str): 버튼 배경색

        Returns:
            tuple: 상태 카드와 버튼 위젯
        """
        card = tk.Frame(
            body,
            bg=card_bg,
            highlightbackground=BORDER,
            highlightthickness=1,
            height=56
        )
        card.pack_propagate(False)

        status_frame = tk.Frame(card, bg=card_bg)
        status_frame.pack(side="left", fill="y", padx=(12, 0))

        tk.Label(
            status_frame,
            text="●",
            bg=card_bg,
            fg=status_color,
            font=("Arial", 12)
        ).pack(side="left", padx=(0, 7), pady=(0, 4))

        tk.Label(
            status_frame,
            text=title,
            bg=card_bg,
            fg=status_color,
            font=("Malgun Gothic", 10, "bold"),
            anchor="center"
        ).pack(side="left")

        button = tk.Button(
            card,
            text=button_text,
            bg=button_bg,
            fg=WHITE,
            disabledforeground=WHITE,
            activebackground=button_bg,
            activeforeground=WHITE,
            relief="flat",
            bd=0,
            font=("Malgun Gothic", 9, "bold"),
            padx=10,
            pady=5
        )
        button.pack(side="right", padx=8, pady=5)

        return card, button

    idle_card, idle_button = create_capture_state(
        "대기 중",
        GRAY,
        GRAY_LIGHT,
        "▶ 촬영 시작",
        BLUE
    )
    idle_card.pack(fill="x", expand=True)

    running_card, running_button = create_capture_state(
        "촬영 중",
        GREEN,
        "#EDF9F2",
        "■ 촬영 중지",
        RED
    )
    running_card.pack_forget()

    def update_capture_state(state):
        """촬영 상태에 따라 화면과 입력 잠금 상태를 갱신합니다.

        Args:
            state (str): 변경된 촬영 상태
        """
        if state == "starting":
            idle_button.configure(
                state=tk.DISABLED,
                text="촬영 시작 대기 중..."
            )
        elif state == "running":
            idle_card.pack_forget()
            running_card.pack(fill="x", expand=True)

            running_button.configure(
                state=tk.NORMAL,
                text="■ 촬영 중지"
            )

            app.capture_ui_lock_manager.set_locked(True)
        elif state == "stopping":
            running_button.configure(
                state=tk.DISABLED,
                text="중지 요청 중..."
            )
        elif state == "idle":
            running_card.pack_forget()
            idle_card.pack(fill="x", expand=True)

            idle_button.configure(
                state=tk.NORMAL,
                text="▶ 촬영 시작"
            )

            app.capture_ui_lock_manager.set_locked(False)

    def update_system_status(status_updates):
        """촬영 처리 결과를 애플리케이션 상태에 반영합니다.

        Args:
            status_updates (dict): 변경할 시스템 상태값
        """
        if "server_status" in status_updates:
            app.state.server_status.set(status_updates["server_status"])

        if "capture_status" in status_updates:
            app.state.capture_status.set(status_updates["capture_status"])

        if "ftp_status" in status_updates:
            app.state.ftp_status.set(status_updates["ftp_status"])

        app.refresh_system_status()

    capture_service = CaptureControlService(
        schedule_callback=app.root.after,
        on_state_change=update_capture_state,
        on_status_change=update_system_status,
        on_notification=lambda message, color=None: app.notify(message, color),
        before_start_capture=before_start_capture
    )

    def start_capture():
        """현재 UI에 입력된 설정으로 촬영을 시작합니다."""
        settings = {
            "hour_text": app.state.hour_var.get(),
            "minute_text": app.state.minute_var.get(),
            "second_text": app.state.second_var.get(),
            "interval_text": app.state.interval_var.get(),
            "storage_mode": app.state.storage_mode.get(),
            "local_path": app.state.local_path.get(),
            "ftp_path": app.state.ftp_path.get()
        }

        capture_service.start_capture(settings)

    def stop_capture():
        """촬영 중지 요청을 Service에 전달합니다."""
        capture_service.stop_capture()

    idle_button.configure(command=start_capture)
    running_button.configure(command=stop_capture)

    return panel
