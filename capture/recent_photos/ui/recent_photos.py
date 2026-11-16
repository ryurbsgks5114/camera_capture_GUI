
import tkinter as tk

from pathlib import Path
from PIL import ImageTk

from config import SUBTEXT

from common.ui.common import create_panel

from capture.recent_photos.service.photo_preview_service import PhotoPreviewService


PLACEHOLDER_PATH = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "no_image.png"
)


def build_photo_preview(parent, view_name):
    """개별 촬영 사진 미리보기 카드를 생성합니다.

    Args:
        parent: 미리보기 카드가 배치될 부모 위젯
        view_name (str): 표시할 카메라 뷰 이름

    Returns:
        dict: 이미지 및 파일명 표시 위젯
    """
    card = tk.Frame(
        parent,
        bg="#FFFFFF",
        highlightbackground="#D8E2EF",
        highlightthickness=1,
        width=300,
        height=330
    )
    card.pack(side="left", fill="y", expand=True, padx=5, pady=6)
    card.pack_propagate(False)

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

    photo_area = tk.Frame(
        card,
        bg="#F7FAFF",
        highlightbackground="#CFDBEB",
        highlightthickness=1,
        width=250,
        height=250
    )
    photo_area.pack(anchor="center", padx=5, pady=(0, 6))
    photo_area.pack_propagate(False)

    placeholder_image = PhotoPreviewService.load_image(PLACEHOLDER_PATH)
    placeholder_image = PhotoPreviewService.resize_image(placeholder_image, (64, 64))

    placeholder_photo = ImageTk.PhotoImage(placeholder_image)

    placeholder_label = tk.Label(
        photo_area,
        image=placeholder_photo,
        bg="#F7FAFF"
    )
    placeholder_label.pack(expand=True, pady=(12, 0))
    placeholder_label.image = placeholder_photo

    filename_label = tk.Label(
        card,
        text="파일명: ",
        bg="#FFFFFF",
        fg=SUBTEXT,
        font=("Malgun Gothic", 8),
        anchor="w"
    )
    filename_label.pack(fill="x", padx=8, pady=(0, 6))

    return {
        "image_label": placeholder_label,
        "filename_label": filename_label
    }


def build(parent, app):
    """최근 촬영 사진 패널을 생성합니다.

    Args:
        parent: 최근 촬영 사진 패널이 배치될 부모 위젯
        app: GUI 애플리케이션 인스턴스
    """
    panel = create_panel(parent, "최근 촬영 사진")
    panel.pack(fill="both", expand=False, pady=(0, 10))

    photo_container = tk.Frame(panel, bg="#FFFFFF")
    photo_container.pack(fill="x", expand=False, padx=8, pady=6)

    app.photo_preview_widgets = {
        "side": build_photo_preview(photo_container, "사이드 뷰"),
        "top": build_photo_preview(photo_container, "탑 뷰")
    }

    for view, widgets in app.photo_preview_widgets.items():
        widgets["image_label"].configure(cursor="hand2")
        widgets["image_label"].bind(
            "<Button-1>",
            lambda event, selected_view=view: open_photo_large(
                app, selected_view
            )
        )


def _update_photo_image(app, view, image, filename):
    """이미지 데이터를 해당 뷰의 미리보기 UI에 반영합니다.

    Args:
        app: GUI 애플리케이션 인스턴스
        view (str): 사진 뷰 구분값
        image (Image.Image): 표시할 이미지
        filename (str): 사진 파일명
    """
    widgets = getattr(app, "photo_preview_widgets", {}).get(view)

    if not widgets:
        return

    try:
        preview_image = PhotoPreviewService.normalize_image(image)

        widgets["original_image"] = preview_image
        widgets["filename"] = filename

        thumbnail_image = PhotoPreviewService.resize_image(preview_image, (250, 250))

        photo = ImageTk.PhotoImage(thumbnail_image)

        image_label = widgets["image_label"]
        image_label.configure(image=photo)
        image_label.image = photo

        widgets["filename_label"].configure(text="파일명: {}".format(filename))
    except (OSError, ValueError) as error:
        print("최근 촬영 사진 표시 실패:", error)


def open_photo_large(app, view):
    """선택한 미리보기 사진을 별도 창에서 확대 표시합니다.

    Args:
        app: GUI 애플리케이션 인스턴스
        view (str): 확대할 사진의 뷰 구분값
    """
    widgets = getattr(app, "photo_preview_widgets", {}).get(view)

    if not widgets:
        return

    preview_image = widgets.get("original_image")

    if preview_image is None:
        return

    filename = widgets.get("filename", "사진")

    display_image = PhotoPreviewService.resize_image(preview_image, (1100, 750))

    preview_window = tk.Toplevel(app.root)
    preview_window.title("사진 확대 보기 - {}".format(filename))
    preview_window.configure(bg="#F5F8FC")
    preview_window.transient(app.root)

    image_width, image_height = display_image.size

    window_width = min(image_width + 40, 1160)
    window_height = min(image_height + 90, 830)

    preview_window.geometry("{}x{}".format(window_width, window_height))
    preview_window.minsize(320, 240)

    tk.Label(
        preview_window,
        text=filename,
        bg="#F5F8FC",
        fg="#183B63",
        font=("Malgun Gothic", 10, "bold"),
        anchor="w"
    ).pack(fill="x", padx=12, pady=(10, 6))

    photo = ImageTk.PhotoImage(display_image)

    image_label = tk.Label(
        preview_window,
        image=photo,
        bg="#F5F8FC"
    )
    image_label.image = photo
    image_label.pack(expand=True, padx=12, pady=(0, 12))

    preview_window.original_image = preview_image


def update_photo(app, view, photo_path):
    """로컬 이미지 파일을 읽어 최근 촬영 사진을 갱신합니다.

    Args:
        app: GUI 애플리케이션 인스턴스
        view (str): 사진 뷰 구분값
        photo_path (str): 이미지 파일 경로
    """
    try:
        image = PhotoPreviewService.load_image(photo_path)

        _update_photo_image(app, view, image, Path(photo_path).name)
    except (OSError, ValueError) as error:
        print("최근 촬영 사진 열기 실패:", error)


def update_photo_from_base64(app, view, filename, encoded_data):
    """Base64 이미지 데이터를 디코딩하여 최근 촬영 사진을 갱신합니다.

    로컬 파일이 없는 FTP 저장 방식에서 실시간 미리보기용으로 사용합니다.

    Args:
        app: GUI 애플리케이션 인스턴스
        view (str): 사진 뷰 구분값
        filename (str): 사진 파일명
        encoded_data (str): Base64 인코딩된 이미지 데이터
    """
    try:
        image = PhotoPreviewService.decode_base64_image(encoded_data)

        _update_photo_image(app, view, image, filename)
    except (ValueError, OSError) as error:
        print("미리보기 데이터 처리 실패:", error)
