
import posixpath
import threading
import tkinter as tk

from tkinter import ttk

from config import WHITE, RED, TEXT, SUBTEXT, BORDER, BLUE

from storage.path.service.ftp_client import list_ftp_directories
from storage.path.service.path_settings_storage import save_path_settings


def open_ftp_browser(app, host, port, user, password):
    """FTP 폴더 선택용 모달 창을 생성합니다.

    Args:
        app (CameraManagerApp): 애플리케이션 인스턴스
        host (str): FTP 서버 주소
        port (int): FTP 서버 포트
        user (str): FTP 로그인 계정
        password (str): FTP 로그인 비밀번호
    """
    dialog = tk.Toplevel(app.root)
    dialog.title("FTP 저장 폴더 선택")
    dialog.geometry("520x440")
    dialog.minsize(420, 340)
    dialog.transient(app.root)
    dialog.grab_set()
    dialog.configure(bg=WHITE)

    current_path = tk.StringVar(value=app.state.ftp_path.get().strip() or "")
    status_text = tk.StringVar(value="FTP 서버에 연결하고 폴더 목록을 불러오는 중...")

    tk.Label(
        dialog,
        text="FTP 저장 폴더 선택",
        bg=WHITE,
        fg=TEXT,
        font=("Malgun Gothic", 13, "bold"),
    ).pack(anchor="w", padx=18, pady=(16, 4))

    tk.Label(
        dialog,
        textvariable=current_path,
        bg=WHITE,
        fg=SUBTEXT,
        font=("Malgun Gothic", 9),
        anchor="w",
    ).pack(fill="x", padx=18, pady=(0, 8))

    list_frame = tk.Frame(
        dialog,
        bg=WHITE,
        highlightbackground=BORDER,
        highlightthickness=1,
    )
    list_frame.pack(fill="both", expand=True, padx=18, pady=4)

    listbox = tk.Listbox(
        list_frame,
        font=("Malgun Gothic", 10),
        activestyle="dotbox",
    )
    scrollbar = ttk.Scrollbar(
        list_frame,
        orient="vertical",
        command=listbox.yview,
    )

    listbox.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    listbox.pack(side="left", fill="both", expand=True)

    tk.Label(
        dialog,
        textvariable=status_text,
        bg=WHITE,
        fg=SUBTEXT,
        font=("Malgun Gothic", 9),
        anchor="w",
    ).pack(fill="x", padx=18, pady=(6, 2))

    button_row = tk.Frame(dialog, bg=WHITE)
    button_row.pack(fill="x", padx=18, pady=(8, 16))

    directories = []
    busy = {"value": False}
    path_is_valid = {"value": False}

    def set_busy(value):
        """FTP 조회 중 조작 버튼의 활성화 상태를 변경합니다.

        Args:
            value (bool): True이면 조작 버튼을 비활성화합니다.
        """
        busy["value"] = value

        for button in (up_button, refresh_button, select_button):
            button.configure(state="disabled" if value else "normal")

    def show_listing(path, allow_home_fallback=False):
        """FTP 폴더 목록을 조회하고 결과를 화면에 표시합니다.

        Args:
            path (str): 조회할 FTP 경로
            allow_home_fallback (bool): 조회 실패 시 기본 경로 재시도 여부
        """
        if busy["value"]:
            return

        set_busy(True)
        status_text.set("FTP 폴더 목록을 불러오는 중...")
        listbox.delete(0, tk.END)

        def worker():
            result = list_ftp_directories(
                host=host,
                port=port,
                user=user,
                password=password,
                remote_path=path,
                timeout=5,
                fallback_to_home=allow_home_fallback,
            )

            def finish():
                """FTP 조회 결과를 메인 스레드에서 화면에 반영합니다."""
                set_busy(False)
                success, message, resolved_path, names = result

                if not success:
                    path_is_valid["value"] = False
                    status_text.set(message)
                    app.notify(message, RED)

                    return

                path_is_valid["value"] = True
                directories[:] = names
                current_path.set(resolved_path or "/")

                listbox.delete(0, tk.END)
                listbox.insert(tk.END, "📁  .. (상위 폴더)")

                for name in directories:
                    listbox.insert(tk.END, "📁  " + name)

                status_text.set(message)

            try:
                dialog.after(0, finish)
            except tk.TclError:
                pass

        threading.Thread(target=worker, daemon=True).start()

    def navigate_selected(event=None):
        """선택한 폴더의 상위 또는 하위 경로로 이동합니다.

        Args:
            event (tk.Event, optional): 리스트박스 이벤트
        """
        selection = listbox.curselection()

        if not selection or busy["value"]:
            return

        index = selection[0]
        path = current_path.get()

        if index == 0:
            parent_path = posixpath.dirname(path.rstrip("/"))

            if not parent_path:
                parent_path = "/"

            show_listing(parent_path)
        else:
            folder_name = directories[index - 1]

            if folder_name.startswith("/"):
                next_path = folder_name
            else:
                next_path = (
                    posixpath.join(path, folder_name)
                    if path != "/"
                    else "/" + folder_name
                )

            show_listing(next_path)

    def select_current_folder():
        """현재 FTP 경로를 저장하고 폴더 선택 창을 닫습니다."""
        if busy["value"]:
            return

        selected_path = current_path.get().strip()

        if not path_is_valid["value"]:
            app.notify("먼저 FTP 폴더 목록을 정상적으로 불러와 주세요.", RED)

            return

        if not selected_path:
            app.notify("FTP 저장 경로를 확인해 주세요.", RED)

            return

        app.state.ftp_path.set(selected_path)

        if save_path_settings(app.state.local_path.get(), app.state.ftp_path.get()):
            app.notify("FTP 저장 경로가 변경되었습니다.")
        else:
            app.notify("경로는 변경되었지만 설정 파일 저장에 실패했습니다.", RED)

        dialog.destroy()

    up_button = tk.Button(
        button_row,
        text="↑ 상위 폴더",
        command=lambda: show_listing(posixpath.dirname(current_path.get().rstrip("/")) or "/"),
        bg=WHITE,
        fg=BLUE,
    )
    up_button.pack(side="left")

    refresh_button = tk.Button(
        button_row,
        text="새로고침",
        command=lambda: show_listing(current_path.get()),
        bg=WHITE,
        fg=BLUE,
    )
    refresh_button.pack(side="left", padx=(6, 0))

    select_button = tk.Button(
        button_row,
        text="이 폴더 선택",
        command=select_current_folder,
        bg=BLUE,
        fg=WHITE,
        activebackground=BLUE,
    )
    select_button.pack(side="right")

    tk.Button(
        button_row,
        text="취소",
        command=dialog.destroy,
        bg=WHITE,
        fg=TEXT,
    ).pack(side="right", padx=(0, 8))

    listbox.bind("<Double-Button-1>", navigate_selected)
    listbox.bind("<Return>", navigate_selected)

    show_listing(current_path.get(), allow_home_fallback=True)
