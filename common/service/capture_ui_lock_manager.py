
class CaptureUiLockManager:
    """촬영 상태에 따른 UI 잠금 대상을 등록하고 관리합니다."""

    def __init__(self):
        """UI 잠금 콜백 관리 목록을 초기화합니다."""
        self._lock_callbacks = {}

    def register(self, name, callback):
        """UI 잠금 콜백을 이름과 함께 등록합니다.

        Args:
            name (str): 잠금 대상 UI의 식별 이름
            callback (Callable): 잠금 여부를 전달받아 UI를 제어하는 함수
        """
        self._lock_callbacks[name] = callback

    def set_locked(self, locked):
        """등록된 모든 UI의 입력을 잠그거나 해제합니다.

        Args:
            locked (bool): True이면 잠그고 False이면 해제합니다.
        """
        for callback in self._lock_callbacks.values():
            callback(locked)
