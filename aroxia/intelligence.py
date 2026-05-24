import time
import asyncio
from collections import deque
import psutil

class IntelligenceModule:
    def __init__(self, tpm_limit=30000, rpm_limit=15):
        self.tpm_limit = tpm_limit # Tokens Per Minute
        self.rpm_limit = rpm_limit # Requests Per Minute
        self.request_timestamps = deque()
        self.token_usage = deque() # (timestamp, count)

    def _clean_old_data(self):
        now = time.time()
        while self.request_timestamps and now - self.request_timestamps[0] > 60:
            self.request_timestamps.popleft()
        while self.token_usage and now - self.token_usage[0][0] > 60:
            self.token_usage.popleft()

    def get_current_rpm(self):
        self._clean_old_data()
        return len(self.request_timestamps)

    def get_current_tpm(self):
        self._clean_old_data()
        return sum(usage for _, usage in self.token_usage)

    async def wait_for_slot(self, estimated_tokens=1000):
        while True:
            self._clean_old_data()
            if self.get_current_rpm() < self.rpm_limit and (self.get_current_tpm() + estimated_tokens) < self.tpm_limit:
                break
            # Calculate backoff
            await asyncio.sleep(1)

    def record_request(self, tokens_used):
        now = time.time()
        self.request_timestamps.append(now)
        self.token_usage.append((now, tokens_used))

    def get_system_health(self):
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory()
            return {
                "rpm": self.get_current_rpm(),
                "tpm": self.get_current_tpm(),
                "load_percent": (self.get_current_rpm() / self.rpm_limit) * 100,
                "cpu_percent": cpu,
                "ram_percent": ram.percent,
                "ram_used_mb": ram.used / (1024 * 1024)
            }
        except Exception:
            return {
                "rpm": self.get_current_rpm(),
                "tpm": self.get_current_tpm(),
                "load_percent": 0,
                "cpu_percent": 0,
                "ram_percent": 0,
                "ram_used_mb": 0
            }
