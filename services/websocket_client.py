import threading
import socketio
from config import SERVER_HOST, SERVER_PORT, WEBSOCKET_RECONNECT_DELAY

# ==========================================
# GUI용 Socket.IO 클라이언트
# UI 변경은 Tkinter 메인 스레드로 전달
# ==========================================
class WebSocketClient:
    def __init__(self, root, on_status, on_test_event):
        self.root = root
        self.on_status = on_status
        self.on_test_event = on_test_event
        self._stop_event = threading.Event()
        self._thread = None
        self._failure_reported = False
        self._last_status = None

        # Socket.IO 클라이언트 인스턴스 초기화(자동 재연결은 아래 _run() 함수에서 관리)
        self.client = socketio.Client(
            reconnection=False,
            logger=False,
            engineio_logger=False
        )

        # ==========================================
        # 서버와 연결 성공 시 호출되는 이벤트 핸들러
        # ==========================================
        @self.client.event
        def connect():
            self._failure_reported = False
            self._dispatch(self.on_status, "연결됨")

        # ==========================================
        # 서버와 연결이 끊겼을 때 호출되는 이벤트 핸들러
        # ==========================================
        @self.client.event
        def disconnect():
            if not self._stop_event.is_set():
                self._dispatch_status("연결 끊김")

        # ==========================================
        # 서버로부터 'ws_test' 이벤트를 수신했을 때 호출되는 핸들러
        # ==========================================
        @self.client.on("ws_test")
        def handle_ws_test(data):
            self._dispatch_event(data)

        # ==========================================
        # 서버에서 실제 사진 촬영 완료 이벤트를 수신하는 핸들러
        # ==========================================
        @self.client.on("photo_saved")
        def handle_photo_saved(data):
            self._dispatch_event(data)

    # ==========================================
    # Tkinter 메인 스레드 안전하게 콜백을 호출하기 위한 헬퍼 함수
    # ==========================================
    def _dispatch(self, callback, value):
        try:
            self.root.after(0, lambda: callback(value))
        except Exception:
            # 창이 이미 닫힌 경우 예약된 UI 작업은 무시한다.
            pass

    def _dispatch_status(self, status):
        # 같은 상태는 main.py로 반복 전달하지 않는다.
        if status == self._last_status:
            return
        self._last_status = status
        self._dispatch(self.on_status, status)

    def _dispatch_event(self, data):
        self._dispatch(self.on_test_event, data)

    # ==========================================
    # WebSocket 클라이언트 백그라운드 스레드 시작 메서드
    # ==========================================
    def start(self):
        if self._thread and self._thread.is_alive():
            return

        self._stop_event.clear()

        self._thread = threading.Thread(
            target=self._run,
            name="WebSocketClientThread",
            daemon=True
        )
        self._thread.start()

    # ==========================================
    # 백그라운드 스레드 메인 루프(서버 연결 유지 및 재연결 관리)
    # ==========================================
    def _run(self):
        url = "http://{}:{}".format(SERVER_HOST, SERVER_PORT)

        while not self._stop_event.is_set():
            try:
                # 연결되어 있지 않은 경우에만 서버 연결 시도
                if not self.client.connected:
                    self.client.connect(url, wait_timeout=5)

                # 연결 유지 상태 대기
                self.client.wait()
            except Exception as error:
                # 종료 이벤트가 설정된 경우 루프 탈출
                if self._stop_event.is_set():
                    break

                if not self._failure_reported:
                    self._failure_reported = True
                    self._dispatch_status("연결 실패")
                
                # 연결 실패 상태 전달
                self._dispatch(self.on_status, "연결 실패")

                # 설정된 재연결 지연 시간만큼 대기 후 재시도
                self._stop_event.wait(WEBSOCKET_RECONNECT_DELAY)

    # ==========================================
    # WebSocket 클라이언트 종료 메서드
    # ==========================================
    def stop(self):
        self._stop_event.set()
        
        try:
            if self.client.connected:
                self.client.disconnect()
        except Exception:
            pass