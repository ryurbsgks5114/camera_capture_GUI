import socketio
import threading

from common.enums.system_status import ConnectionStatus
from config import SERVER_HOST, SERVER_PORT, WEBSOCKET_RECONNECT_DELAY


class WebSocketClient:
    """GUI와 서버 간 Socket.IO 연결 및 이벤트 수신을 관리합니다.

    서버 연결 상태와 촬영 완료 이벤트를 수신하며,
    Tkinter UI 콜백은 root.after()를 통해 전달합니다.

    Args:
        root (tk.Tk): 애플리케이션 최상위 Tkinter 객체
        on_status (callable): 연결 상태 변경 시 실행할 콜백
        on_event (callable): 서버 이벤트 수신 시 실행할 콜백
    """
    def __init__(self, root, on_status, on_event):
        """WebSocket 클라이언트와 이벤트 핸들러를 초기화합니다."""
        self.root = root
        self.on_status = on_status
        self.on_event = on_event

        self._stop_event = threading.Event()
        self._thread = None
        self._failure_reported = False
        self._last_status = None

        self.client = socketio.Client(
            reconnection=False,
            logger=False,
            engineio_logger=False
        )

        @self.client.event
        def connect():
            """서버와 연결되었을 때 연결 상태를 전달합니다."""
            self._failure_reported = False
            self._dispatch(
                self.on_status,
                ConnectionStatus.CONNECTED.value,
            )

        @self.client.event
        def disconnect():
            """서버 연결이 끊겼을 때 연결 끊김 상태를 전달합니다."""
            if not self._stop_event.is_set():
                self._dispatch_status(ConnectionStatus.DISCONNECTED.value)

        @self.client.on("photo_saved")
        def handle_photo_saved(data):
            """서버에서 사진 저장 완료 이벤트를 수신합니다.

            Args:
                data (dict): 서버에서 전달한 사진 저장 이벤트 데이터
            """
            self._dispatch_event(data)

    def _dispatch(self, callback, value):
        """Tkinter 메인 스레드에서 콜백을 실행하도록 예약합니다.

        종료 요청 이후에는 새로운 UI 작업을 예약하지 않습니다.

        Args:
            callback (callable): 실행할 콜백 함수
            value: 콜백에 전달할 데이터
        """
        if self._stop_event.is_set():
            return

        try:
            self.root.after(0, lambda: callback(value))
        except Exception:
            pass

    def _dispatch_status(self, status):
        """변경된 연결 상태를 UI 콜백으로 전달합니다.

        동일한 상태가 반복 전달되는 것을 방지합니다.

        Args:
            status (str): 전달할 연결 상태
        """
        if status == self._last_status:
            return

        self._last_status = status
        self._dispatch(self.on_status, status)

    def _dispatch_event(self, data):
        """서버 이벤트 데이터를 UI 콜백으로 전달합니다.

        Args:
            data: 서버에서 수신한 이벤트 데이터
        """
        self._dispatch(self.on_event, data)

    def start(self):
        """WebSocket 연결 관리용 백그라운드 스레드를 시작합니다."""
        if self._thread and self._thread.is_alive():
            return

        self._stop_event.clear()

        self._thread = threading.Thread(
            target=self._run,
            name="WebSocketClientThread",
            daemon=True
        )
        self._thread.start()

    def _run(self):
        """서버 연결을 유지하고 연결이 끊기면 재연결을 시도합니다."""
        url = "http://{}:{}".format(SERVER_HOST, SERVER_PORT)

        while not self._stop_event.is_set():
            try:
                if not self.client.connected:
                    self.client.connect(url, wait_timeout=5)

                if self._stop_event.is_set():
                    break

                self.client.wait()
            except Exception:
                if self._stop_event.is_set():
                    break

                if not self._failure_reported:
                    self._failure_reported = True
                    self._dispatch_status(ConnectionStatus.FAILED.value)

                self._stop_event.wait(WEBSOCKET_RECONNECT_DELAY)

    def _disconnect(self):
        """서버와의 WebSocket 연결을 해제합니다."""
        try:
            if self.client.connected:
                self.client.disconnect()
        except Exception:
            pass

    def stop(self):
        """WebSocket 클라이언트를 종료하고 재연결을 중단합니다."""
        self._stop_event.set()

        threading.Thread(
            target=self._disconnect,
            name="WebSocketDisconnectThread",
            daemon=True
        ).start()
        