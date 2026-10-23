# Camera Manager - Windows GUI 애플리케이션

라즈베리파이 카메라 촬영 서버를 설정하고 제어하는 Tkinter 기반 Windows GUI 애플리케이션입니다.<br>
HTTP API로 촬영을 시작·중지하고, WebSocket으로 서버 연결 상태 및 이벤트를 수신합니다.

## 폴더 및 파일 구조

```text
camera_capture_GUI/
├── main.py                           # GUI 진입점, 화면 조립, WebSocket 콜백 및 종료 처리
├── config.py                         # 창/색상/서버 주소/FTP 기본값/촬영 기본값 설정
├── state.py                          # GUI 입력값과 상태를 보관하는 Tkinter 변수
├── secret_config.example.py          # FTP 민감정보 설정 파일 예시(값 입력 후 'example.' 부분 삭제)
├── services/                         # 서버 통신, 검증 및 외부 서비스 로직
│   ├── api_client.py                 # 서버 HTTP API 요청(/status, /start, /stop 등)
│   ├── capture_settings_validator.py # 촬영 설정 입력값 검증
│   ├── capture_start_validator.py    # 촬영 시작 전 필수 설정 검증
│   ├── ftp_client.py                 # FTP 서버 연결 및 폴더/파일 관련 처리
│   ├── ftp_validator.py              # FTP 설정값 검증
│   ├── path_validator.py             # 로컬 저장 경로 검증
│   └── websocket_client.py           # WebSocket 연결·재연결 및 서버 이벤트 수신
└── ui/                               # GUI 화면 구성 모듈
    ├── common.py                     # 공통 UI 스타일, 패널/입력 요소 생성 도우미
    ├── layout.py                     # 전체 화면 레이아웃과 헤더 구성
    ├── system_status.py              # 시스템 상태 표시(서버, WebSocket, 촬영, FTP )
    ├── server_connection.py          # 서버 연결 UI
    ├── ftp_settings.py               # FTP 설정 UI
    ├── ftp_browser.py                # FTP 폴더 탐색 UI
    ├── save_path.py                  # 저장 경로 설정 UI
    ├── capture_settings.py           # 촬영 설정 UI
    ├── storage_mode.py               # 저장 방식 UI
    ├── capture_control.py            # 촬영 제어 UI
    ├── recent_photos.py              # 최근 촬영 사진 UI(실제 사진 이벤트 연동 전)
    └── notifications.py              # 알림 UI
```

## 의존성 설치

PowerShell에서 프로젝트 폴더로 이동합니다.

```powershell
cd 경로\camera_capture_GUI
```

WebSocket 클라이언트 의존성을 설치합니다.<br>
`requests`는 Socket.IO의 HTTP polling 연결에 필요합니다.

```powershell
python -m pip install --upgrade pip
python -m pip install "python-socketio==5.11.0" "python-engineio==4.8.0" "requests" "websocket-client==1.6.4"
```

## 실행 방법

```powershell
python main.py
```