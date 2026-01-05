# src/http_client.py
import time
import requests
from typing import Any, Dict, Optional

class HttpClient:
    def __init__(self, timeout_sec: int, sleep_sec: float = 0.0):
        self.timeout_sec = timeout_sec
        self.sleep_sec = sleep_sec

    def get_json(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        resp = requests.get(url, params=params, timeout=self.timeout_sec)
        resp.raise_for_status()
        if self.sleep_sec:
            time.sleep(self.sleep_sec)
        return resp.json()
