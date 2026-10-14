import posixpath
import threading
import tkinter as tk
from tkinter import ttk
from config import WHITE, RED, TEXT, SUBTEXT, BORDER, BLUE
from services.ftp_client import list_ftp_directories 
    
# FTP 서버의 디렉토리를 탐색하고 선택할 수 있는 팝업 창을 생성하는 함수
def open_ftp_browser(app, host, port, user, password):
    # FTP 서버 폴더 선택용 모달 창 설정
    dialog = tk.Toplevel(app.root)
    dialog.title("FTP 저장 폴더 선택")
    dialog.geometry("520x440")
    dialog.minsize(420, 340)
    dialog.transient(app.root)
    dialog.grab_set()
    dialog.configure(bg=WHITE)

    current_path = tk.StringVar(value=app.state.ftp_path.get().strip() or "")
    status_text = tk.StringVar(value="FTP 서버에 연결하고 폴더 목록을 불러오는 중...")

    # 모달 창 상단 타이틀 및 현재 경로 표시
    tk.Label(
        dialog,
        text="FTP 저장 폴더 선택",
        bg=WHITE,
        fg=TEXT,
        font=("Malgun Gothic", 13, "bold")
    ).pack(anchor="w", padx=18, pady=(16, 4))
    tk.Label(
        dialog,
        textvariable=current_path,
        bg=WHITE,
        fg=SUBTEXT,
        font=("Malgun Gothic", 9),
        anchor="w"
    ).pack(fill="x", padx=18, pady=(0, 8))

    # 폴더 목록을 표시할 리스트박스 및 스크롤바 프레임
    list_frame = tk.Frame(dialog, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
    list_frame.pack(fill="both", expand=True, padx=18, pady=4)
    listbox = tk.Listbox(list_frame, font=("Malgun Gothic", 10), activestyle="dotbox")
    scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=listbox.yview)
    listbox.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    listbox.pack(side="left", fill="both", expand=True)

    # 하단 상태 메시지
    tk.Label(
        dialog,
        textvariable=status_text,
        bg=WHITE,
        fg=SUBTEXT,
        font=("Malgun Gothic", 9),
        anchor="w"
    ).pack(fill="x", padx=18, pady=(6, 2))

    # 하단 조작 버튼들을 담을 프레임
    button_row = tk.Frame(dialog, bg=WHITE)
    button_row.pack(fill="x", padx=18, pady=(8, 16))

    directories = []
    busy = {"value": False}
    path_is_valid = {"value": False}

    # 통신 중복 방지를 위한 버튼 활성화/비활성화 제어 함수
    def set_busy(value):
        busy["value"] = value

        for button in (up_button, refresh_button, select_button):
            button.configure(state="disabled" if value else "normal")

    # 지정된 경로의 FTP 폴더 목록을 비동기로 불러와 리스트박스에 렌더링하는 함수
    def show_listing(path, allow_home_fallback=False):
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
                timeout=5
            )

            # 저장된 경로가 더 이상 유효하지 않으면 FTP 로그인 기본 경로로 재시도
            if not result[0] and allow_home_fallback and path:
                fallback = list_ftp_directories(
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    remote_path="",
                    timeout=5
                )

                if fallback[0]:
                    result = fallback
                    result = (result[0], "저장된 경로에 접근할 수 없어 FTP 기본 경로를 표시합니다.", result[2], result[3])

            # 작업 완료 후 메인 스레드에서 UI를 갱신하는 함수
            def finish():
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

    # 모달 창 항목 더블 클릭 또는 Enter 입력 시 해당 폴더로 이동하는 함수
    def navigate_selected(event=None):
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
                next_path = posixpath.join(path, folder_name) if path != "/" else "/" + folder_name

            show_listing(next_path)

    # '이 폴더 선택' 버튼 클릭 시 현재 경로를 최종 선택하고 창을 닫는 함수
    def select_current_folder():
        if busy["value"]:
            return

        selected_path = current_path.get().strip()

        if not path_is_valid["value"]:
            app.notify("먼저 FTP 폴더 목록을 정상적으로 불러와 주세요.", RED)
            return
        if not selected_path:
            app.notify("FTP 저장 경로를 확인해 주세요.", RED)
            return

        # 선택 시점에도 해당 경로의 접속 및 조회가 성공한 경로만 저장합니다.
        app.state.ftp_path.set(selected_path)
        app.notify("FTP 저장 경로가 변경되었습니다.")
        dialog.destroy()

    # 모달 창 하단 제어 버튼들 생성 및 배치
    up_button = tk.Button(
        button_row,
        text="↑ 상위 폴더",
        command=lambda: show_listing(posixpath.dirname(current_path.get().rstrip("/")) or "/"),
        bg=WHITE,
        fg=BLUE
    )
    up_button.pack(side="left")

    refresh_button = tk.Button(
        button_row,
        text="새로고침",
        command=lambda: show_listing(current_path.get()),
        bg=WHITE,
        fg=BLUE
    )
    refresh_button.pack(side="left", padx=(6, 0))

    select_button = tk.Button(
        button_row,
        text="이 폴더 선택",
        command=select_current_folder,
        bg=BLUE,
        fg=WHITE,
        activebackground=BLUE
    )
    select_button.pack(side="right")

    tk.Button(
        button_row,
        text="취소",
        command=dialog.destroy,
        bg=WHITE,
        fg=TEXT
    ).pack(side="right", padx=(0, 8))

    # 리스트박스 이벤트 바인딩 및 최초 목록 로드 수행
    listbox.bind("<Double-Button-1>", navigate_selected)
    listbox.bind("<Return>", navigate_selected)
    show_listing(current_path.get(), allow_home_fallback=True)