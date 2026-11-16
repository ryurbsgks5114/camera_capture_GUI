
import base64
import io

from PIL import Image


class PhotoPreviewService:
    """최근 촬영 사진의 이미지 데이터를 읽고 가공합니다."""
    @staticmethod
    def load_image(photo_path):
        """이미지 파일을 읽어 독립적인 이미지 객체로 반환합니다.

        Args:
            photo_path (str): 이미지 파일 경로

        Returns:
            Image.Image: 읽어온 이미지 객체
        """
        with Image.open(photo_path) as source:
            return source.copy()

    @staticmethod
    def decode_base64_image(encoded_data):
        """Base64 문자열을 이미지 객체로 변환합니다.

        Args:
            encoded_data (str): Base64 인코딩된 이미지 데이터

        Returns:
            Image.Image: 디코딩된 이미지 객체
        """
        photo_data = base64.b64decode(encoded_data, validate=True)

        with Image.open(io.BytesIO(photo_data)) as source:
            return source.copy()

    @staticmethod
    def normalize_image(image):
        """이미지를 RGB 모드로 변환한 복사본을 반환합니다.

        Args:
            image (Image.Image): 변환할 이미지

        Returns:
            Image.Image: RGB 모드 이미지
        """
        return image.convert("RGB").copy()

    @staticmethod
    def resize_image(image, size):
        """원본 비율을 유지하면서 이미지 크기를 조절합니다.

        Args:
            image (Image.Image): 크기를 조절할 이미지
            size (tuple): 최대 가로 및 세로 크기

        Returns:
            Image.Image: 크기가 조절된 이미지 복사본
        """
        resampling = getattr(Image, "Resampling", Image)

        resized_image = image.copy()
        resized_image.thumbnail(size, resampling.LANCZOS)

        return resized_image
