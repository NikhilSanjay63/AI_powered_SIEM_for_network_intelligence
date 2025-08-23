import time
import json
import threading
from collections import Counter
import os

LOG_DB_PATH = os.path.join(os.path.dirname(__file__), "logs.json")
BLOCKED_IPS_PATH = os.path.join(os.path.dirname(__file__), "blocked_ips.json")

class AIBrainSIEM:
    def __init__(self):
        self.baseline_counts = []
        self.mean = 0
        self.std = 1
        self.blocked_ips = set()
        self.learning_phase = True
        self.lock = threading.Lock()

    def query_event_count(self, seconds=1):
        now = time.time()
        try:
            with open(LOG_DB_PATH, "r") as f:
                logs = json.load(f)
        except Exception:
            logs = []
        return sum(1 for log in logs if self._timestamp_to_epoch(log["timestamp"]) >= now - seconds)

    def query_events(self, seconds=10):
        now = time.time()
        try:
            with open(LOG_DB_PATH, "r") as f:
                logs = json.load(f)
        except Exception:
            logs = []
        return [log for log in logs if self._timestamp_to_epoch(log["timestamp"]) >= now - seconds]

    def _timestamp_to_epoch(self, ts):
        from datetime import datetime
        try:
            return datetime.fromisoformat(ts).timestamp()
        except Exception:
            return 0

    def learn_baseline(self, duration=30):
        print("Learning phase started...")
        for _ in range(duration):
            count = self.query_event_count(seconds=1)
            self.baseline_counts.append(count)
            time.sleep(1)
        self.mean = sum(self.baseline_counts) / len(self.baseline_counts)
        variance = sum((x - self.mean) ** 2 for x in self.baseline_counts) / len(self.baseline_counts)
        self.std = variance ** 0.5 if variance > 0 else 1
        self.learning_phase = False
        print(f"Learning complete. Baseline mean: {self.mean:.2f}, std: {self.std:.2f}")

    def monitor(self):
        print("Monitoring phase started...")
        while True:
            try:
                current_count = self.query_event_count(seconds=1)
                # Ensure std is never zero
                std = self.std if self.std > 0 else 1
                z_score = (current_count - self.mean) / std
                print(f"Current event count: {current_count}, Z-score: {z_score:.2f}")
                if z_score > 3.5:
                    print("Attack detected! Pinpointing malicious IPs...")
                    self.detect_and_block()
                time.sleep(1)
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(1)

    def detect_and_block(self):
        recent_events = self.query_events(seconds=10)
        ip_counts = Counter(log["src_ip"] for log in recent_events)
        for ip, count in ip_counts.items():
            if count > 5:
                protocols = [log["protocol"] for log in recent_events if log["src_ip"] == ip]
                protocol_counts = Counter(protocols)
                total_protocols = len(protocols)
                icmp_percentage = (protocol_counts.get("ICMP", 0) / total_protocols) * 100
                udp_percentage = (protocol_counts.get("UDP", 0) / total_protocols) * 100

                if icmp_percentage > 50 or udp_percentage > 50:
                    self.blocked_ips.add(ip)
        self.save_blocked_ips()
        print(f"Blocked IPs: {list(self.blocked_ips)}")

    def save_blocked_ips(self):
        # Load existing history
        try:
            with open(BLOCKED_IPS_PATH, "r") as f:
                history = set(json.load(f))
        except Exception:
            history = set()
        # Add new blocked IPs
        history.update(self.blocked_ips)
        with open(BLOCKED_IPS_PATH, "w") as f:
            json.dump(list(history), f, indent=2)

if __name__ == "__main__":
    ai_brain = AIBrainSIEM()
    ai_brain.learn_baseline(duration=30)
    ai_brain.monitor()