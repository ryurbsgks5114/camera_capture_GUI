# Camera Manager — Windows GUI

라즈베리파이 카메라 촬영 서버를 설정하고 제어하는 Tkinter 기반 Windows GUI 애플리케이션입니다. HTTP API로 촬영을 시작·중지하고, WebSocket으로 서버 연결 상태 및 이벤트를 수신합니다.

## 현재 구현 상태

- GUI 화면 구성 및 촬영 설정 입력
- HTTP API를 통한 서버 상태 확인과 촬영 시작·중지 요청
- FTP 설정 및 FTP 브라우저 관련 화면/클라이언트
- WebSocket 연결, 연결 상태 알림, 재연결 시도
- 현재는 WebSocket 연결 테스트 이벤트(`ws_test`)를 수신하는 단계입니다.
- 실제 사진 저장 이벤트 수신과 사진 파일 다운로드는 아직 구현 전입니다.

## 폴더 및 파일 구조

```text
camera_capture_GUI/
├── main.py                           # GUI 진입점, 화면 조립, WebSocket 콜백 및 종료 처리
├── config.py                         # 창/색상/서버 주소/FTP 기본값/촬영 기본값 설정
├── state.py                          # GUI 입력값과 상태를 보관하는 Tkinter 변수
├── secret_config.example.py          # FTP 민감정보 설정 파일 예시(복사 후 값 입력)
├── .gitignore                        # Python 캐시 및 secret_config.py 제외
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
    ├── system_status.py              # 서버 및 WebSocket 상태 표시
    ├── server_connection.py          # 서버 주소/연결 설정 UI
    ├── ftp_settings.py               # FTP 설정 UI
    ├── ftp_browser.py                # FTP 폴더 탐색 UI
    ├── save_path.py                  # 로컬 사진 저장 경로 UI
    ├── capture_settings.py           # 촬영 시작 시간 및 간격 설정 UI
    ├── storage_mode.py               # local / ftp / both 저장 방식 선택 UI
    ├── capture_control.py            # 촬영 시작·중지 제어 UI
    ├── recent_photos.py              # 최근 사진 표시 영역(실제 사진 이벤트 연동 전)
    └── notifications.py              # 사용자 알림 영역
```

## 요구 환경

- Windows 10/11 권장
- Python 3.7 이상 권장(사용 중인 Python/Tkinter 환경에서 실행 확인 필요)
- Tkinter: 일반적인 Windows Python 설치에 포함됨
- Raspberry Pi 서버와 GUI PC가 네트워크로 통신할 수 있어야 함

## 설치 방법 (requirements.txt 미사용)

PowerShell에서 프로젝트 폴더로 이동합니다.

```powershell
cd 경로\camera_capture_GUI
python --version
```

가상환경 사용을 원하면(선택):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

WebSocket 클라이언트 의존성을 설치합니다. `requests`는 Socket.IO의 HTTP polling 연결에 필요합니다.

```powershell
python -m pip install --upgrade pip
python -m pip install "python-socketio==5.11.0" "python-engineio==4.8.0" "requests" "websocket-client==1.6.4"
```

## 민감정보 설정

1. 프로젝트 루트에서 예시 파일을 복사합니다.

```powershell
Copy-Item secret_config.example.py secret_config.py
```

2. `secret_config.py`를 열어 실제 FTP 값을 입력합니다. `FTP_PORT`는 따옴표 없는 정수(예: `21`)로 입력해야 합니다.

```python
FTP_HOST = "FTP 서버 주소"
FTP_PORT = 21
FTP_USER = "FTP 계정"
FTP_PASSWORD = "FTP 비밀번호"
```

3. `config.py`의 `SERVER_HOST`와 `SERVER_PORT`가 실제 Raspberry Pi 서버 주소와 일치하는지 확인합니다.

> `secret_config.py`에는 비밀번호가 들어가므로 GitHub에 커밋하지 마세요. `.gitignore`에서 제외하도록 설정되어 있습니다.

## 실행 방법

```powershell
python main.py
```

GUI가 실행되면 서버 연결 상태를 확인합니다. 서버가 꺼져 있으면 연결 실패 상태가 표시되고, 서버가 실행되면 재연결을 시도합니다.

## 개발 메모

- WebSocket 테스트 이벤트는 실제 `photo_saved` 이벤트 수신이 구현되고 검증된 뒤 정리할 예정입니다.
- GUI를 닫을 때 촬영 중지 API까지 호출하는 처리는 아직 다음 개발 단계에서 구현할 예정입니다.
- Windows 실행 파일(`.exe`) 패키징은 통합 테스트 후 진행합니다.
