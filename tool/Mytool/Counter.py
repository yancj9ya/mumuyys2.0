import time
from PIGEON.log import Log

log = Log()


class Counter:
    COUNTER_RECORD = {}

    def __init__(self, name=None):
        try:
            self.name = name
            self.count = 0
            self.start_time = time.time() - 5
        except Exception as e:
            log.error(f"Initialization Error: {e}")

    def compare(self, compare_num):
        """
        Compare the current count with the given number.
        If the current count is less than the given number, return True."""
        try:
            if self.count >= compare_num:
                return True
            else:
                return False
        except Exception as e:
            log.error(f"Compare Error: {e}")

    def increment(self, interval=10):
        try:
            current_time = time.time()
            if current_time - self.start_time > interval:
                self.count += 1
                self.start_time = current_time
                return True
            else:
                return False
        except Exception as e:
            log.error(f"Increment Error: {e}")

    def reset(self):
        try:
            self.count = 0
            self.start_time = time.time() - 5
            log.debug(f"Counter {self.name if self.name else ''} Reset")
        except Exception as e:
            log.error(f"Reset Error: {e}")

    def add_record(self, record_name: str):
        try:
            if record_name in self.COUNTER_RECORD:
                self.COUNTER_RECORD[record_name] = self.count
            else:
                self.COUNTER_RECORD[record_name] = self.count
            log.info(f"Record {record_name} added")
        except Exception as e:
            log.error(f"Add Record Error: {e}")

    def get_record(self, record_name: str):
        try:
            if record_name in self.COUNTER_RECORD:
                return self.COUNTER_RECORD[record_name]
            else:
                return None
        except Exception as e:
            log.error(f"Get Record Error: {e}")
