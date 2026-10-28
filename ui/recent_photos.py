import base64
import io
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
# 사진 미리보기 카드 생성 및 위젯 참조 반환 함수
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

    return {
        "image_label": placeholder_label,
        "filename_label": filename_label
    }

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

    # 사이드 뷰 및 탑 뷰 썸네일 카드 생성하고 내부 위젯 참조를 딕셔너리로 저장
    app.photo_preview_widgets = {
        "side": build_photo_preview(photo_container, "사이드 뷰"),
        "top": build_photo_preview(photo_container, "탑 뷰")
    }

    # 썸네일 클릭 이벤트 바인딩(마우스 커서 변경 및 클릭 시 원본 확대 창 열기)
    for view, widgets in app.photo_preview_widgets.items():
        widgets["image_label"].configure(cursor="hand2")
        widgets["image_label"].bind(
            "<Button-1>",
            lambda event, selected_view=view: open_photo_large(
                app, selected_view
            )
        )

# ==========================================
# 이미지 객체를 받아 원본을 보관하고 썸네일로 변환하여 화면에 표시하는 함수
# ==========================================
def _update_photo_image(app, view, image, filename):
    # 앱 객체에 저장된 썸네일 위젯 딕셔너리에서 해당 뷰의 위젯들을 가져옴
    widgets = getattr(app, "photo_preview_widgets", {}).get(view)

    if not widgets:
        return

    try:
        # 전달받은 이미지를 RGB 모드로 변환 후 원본 복사본으로 저장(확대 보기용)
        original_image = image.convert("RGB").copy()

        widgets["original_image"] = original_image
        widgets["filename"] = filename

        # Pillow 버전 호환성을 고려하여 LANCZOS 리샘플링 방식 설정
        resampling = getattr(Image, "Resampling", Image)

        thumbnail_image = original_image.copy()
        # 썸네일 영역 규격에 맞춰 비율을 유지하며 썸네일 크기로 조절
        thumbnail_image.thumbnail((250, 250), resampling.LANCZOS)

        # Tkinter에서 렌더링할 수 있는 사진 객체로 변환
        photo = ImageTk.PhotoImage(thumbnail_image)

        # 이미지 표시 레이블에 생성된 사진 적용
        image_label = widgets["image_label"]
        image_label.configure(image=photo)
        image_label.image = photo

        # 파일명 텍스트 갱신
        widgets["filename_label"].configure(text="파일명: {}".format(filename))
    except (OSError, ValueError) as error:
        print("최근 촬영 사진 표시 실패:", error)

# ==========================================
# 썸네일 클릭 시 원본 사진을 큰 창으로 띄워주는 함수
# ==========================================
def open_photo_large(app, view):
    # 선택한 뷰의 위젯 정보 가져오기
    widgets = getattr(app, "photo_preview_widgets", {}).get(view)

    if not widgets:
        return

    # 저장되어 있는 원본 이미지 확인
    original_image = widgets.get("original_image")

    # 아직 촬영된 사진이 없으면 확대 창을 열지 않음
    if original_image is None:
        return

    filename = widgets.get("filename", "사진")

    # 원본 이미지 데이터는 보호하고, 확대 창 표시용 복사본 생성 후 적정 규격으로 크기 조절
    display_image = original_image.copy()

    resampling = getattr(Image, "Resampling", Image)
    display_image.thumbnail((1100, 750), resampling.LANCZOS)

    # Toplevel을 이용해 독립된 사진 확대 보기 창 생성
    preview_window = tk.Toplevel(app.root)
    preview_window.title("사진 확대 보기 - {}".format(filename))
    preview_window.configure(bg="#F5F8FC")
    preview_window.transient(app.root)

    # 이미지 규격에 맞춰 확대 창의 가로/세로 크기 동적 계산 및 설정
    image_width, image_height = display_image.size

    window_width = min(image_width + 40, 1160)
    window_height = min(image_height + 90, 830)

    preview_window.geometry("{}x{}".format(window_width, window_height))
    preview_window.minsize(320, 240)

    # 확대 창 상단에 파일명 표시
    tk.Label(
        preview_window,
        text=filename,
        bg="#F5F8FC",
        fg="#183B63",
        font=("Malgun Gothic", 10, "bold"),
        anchor="w"
    ).pack(fill="x", padx=12, pady=(10, 6))

    # 확대된 사진을 표시할 레이블 생성 및 Tkinter 이미지 객체 바인딩
    photo = ImageTk.PhotoImage(display_image)

    image_label = tk.Label(preview_window, image=photo, bg="#F5F8FC")
    image_label.image = photo
    image_label.pack(expand=True, padx=12, pady=(0, 12))

    # 창이 열려 있는 동안 이미지 참조 유지
    preview_window.original_image = original_image

# ==========================================
# 로컬에 저장된 사진으로 썸네일 갱신
# ==========================================
def update_photo(app, view, photo_path):
    try:
        # 지정된 경로의 로컬 이미지 파일을 열어 메모리에 복사본 생성
        with Image.open(photo_path) as source:
            image = source.copy()

        # _update_photo_image 함수를 호출하여 화면에 이미지 및 파일명 반영
        _update_photo_image(app, view, image, Path(photo_path).name)
    except (OSError, ValueError) as error:
        print("최근 촬영 사진 열기 실패:", error)

# ==========================================
# 메모리에 전달된 Base64 인코딩 데이터를 디코딩하여 미리보기 갱신
# 로컬에 파일이 없을 때(FTP 저장 방식 일 때) 실시간 프리뷰용으로 사용
# ==========================================
def update_photo_from_base64(app, view, filename, encoded_data):
    try:
        # Base64 문자열을 바이트 데이터로 디코딩
        photo_data = base64.b64decode(encoded_data, validate=True)

        # 바이트 데이터를 가상의 메모리 스트림(BytesIO)으로 읽어와 이미지 객체 생성
        with Image.open(io.BytesIO(photo_data)) as source:
            image = source.copy()

        # _update_photo_image 함수를 호출하여 화면에 이미지 및 파일명 반영
        _update_photo_image(app, view, image, filename)
    except (ValueError, OSError) as error:
        print("미리보기 데이터 처리 실패:", error)