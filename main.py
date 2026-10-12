import tkinter as tk

from config import APP_TITLE, WINDOW_GEOMETRY, WINDOW_MIN_SIZE, BG
from state import AppState
from ui.common import configure_style
from ui.layout import build_header, build_main
from ui import system_status, server_connection, ftp_settings, save_path
from ui import capture_settings, storage_mode, capture_control
from ui import recent_photos, notifications


class CameraManagerApp:
    def __init__(self, root):
        self.root = root
        self.state = AppState(root)
        self.vcmd = (root.register(self.validate_number), "%P")
        self.notify = lambda message, color=None: None

        configure_style()
        build_header(root)
        _, left, center, right = build_main(root)

        system_status.build(left, self)
        server_connection.build(left, self)
        ftp_settings.build(left, self)
        save_path.build(left, self)

        capture_settings.build(center, self)
        storage_mode.build(center, self)
        capture_control.build(center, self)

        recent_photos.build(right, self)
        notifications.build(right, self)

    @staticmethod
    def validate_number(value):
        return value.isdigit() or value == ""

    def refresh_system_status(self):
        system_status.refresh(self)


def main():
    root = tk.Tk()
    root.title(APP_TITLE)
    root.geometry(WINDOW_GEOMETRY)
    root.minsize(*WINDOW_MIN_SIZE)
    root.configure(bg=BG)

    CameraManagerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
