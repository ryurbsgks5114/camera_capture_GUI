# 📷 Camera Manager - GUI 애플리케이션

라즈베리파이 기반의 카메라 관리 시스템을 원격으로 조작하고 모니터링하기 위한 윈도우 데스크톱 GUI 애플리케이션입니다.

---

## 📂 폴더 구조 (Directory Structure)

```text
camera_manager_split/
│
├─ main.py                    # 프로그램 시작 및 전체 UI 조립
├─ config.py                  # 전역 색상 및 창 크기 등 설정
├─ state.py                   # GUI 초기 상태값 관리
│
├─ ui/                        # 화면 구성요소 패널 및 위젯 모듈
│   ├─ common.py              # 공통 UI 컴포넌트 (패널, 필드, 버튼 등)
│   ├─ layout.py              # 전체 레이아웃 배치
│   ├─ system_status.py       # 시스템 상태 모니터링
│   ├─ server_connection.py   # 서버 연결 정보 설정
│   ├─ ftp_settings.py        # FTP 서버 설정
│   ├─ save_path.py           # 사진 저장 경로 설정
│   ├─ capture_settings.py    # 촬영 시간 및 간격 설정
│   ├─ storage_mode.py        # 저장 방식 선택 (Local / FTP / Both)
│   ├─ capture_control.py     # 촬영 시작 및 중지 제어 버튼
│   ├─ recent_photos.py       # 최근 촬영된 사진 미리보기 영역
│   └─ notifications.py       # 알림 메시지 영역
│
└─ services/                  # 통신 및 외부 서비스 연동 모듈
    ├─ api_client.py          # 라즈베리파이 서버와의 HTTP API 통신
    └─ ftp_client.py          # FTP 파일 전송 관련 클라이언트 로직