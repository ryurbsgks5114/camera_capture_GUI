import json
from urllib.request import Request, urlopen
from config import SERVER_HOST, SERVER_PORT, SERVER_TIMEOUT

# ==========================================
# 라즈베리파이 서버 상태 조회 함수
# ==========================================
def get_server_status():

    url = "http://{}:{}/status".format(SERVER_HOST, SERVER_PORT)

    request = Request(
        url,
        headers={"Accept": "application/json"},
        method="GET"
    )

    with urlopen(request, timeout=SERVER_TIMEOUT) as response:
        if response.status != 200:
            raise RuntimeError("HTTP Status: {}".format(response.status))

        data = json.loads(response.read().decode("utf-8"))

    return data