"""S7-300 PLC Simulator for testing."""
import time, threading
from typing import Optional

class PLCSimulator:
    """Emulates Siemens S7-300 DB memory with trigger and heartbeat."""

    def __init__(self):
        self.db1_trigger = False
        self.db1_trigger_seq = 0
        self.db1_station_id = 1
        self.db2_ok = False
        self.db2_ng = False
        self.db2_error_code = 0
        self.db2_defect_class = 0
        self.db3_edge_ping = False
        self.db3_plc_pong = False
        self.db3_timestamp = 0
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._running = False

    def start(self):
        self._running = True
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()

    def stop(self):
        self._running = False

    def _heartbeat_loop(self):
        while self._running:
            time.sleep(3)
            if self._running:
                self.db3_plc_pong = self.db3_edge_ping
                self.db3_timestamp = int(time.time() % 86400)

    def simulate_trigger(self, station_id: int = 1):
        self.db1_trigger = True
        self.db1_trigger_seq += 1
        self.db1_station_id = station_id

    def clear_trigger(self):
        self.db1_trigger = False

    def write_result_ok(self):
        self.db2_ok = True
        self.db2_ng = False
        self.db2_error_code = 0

    def write_result_ng(self, error_code: int = 1, defect_class: int = 0):
        self.db2_ok = False
        self.db2_ng = True
        self.db2_error_code = error_code
        self.db2_defect_class = defect_class

    def reset_result(self):
        self.db2_ok = False
        self.db2_ng = False
        self.db2_error_code = 0
        self.db2_defect_class = 0
