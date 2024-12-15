# contrl task for start wait and stop

from threading import Lock


class MyEvent:

    evet_dict = {}

    def __init__(self, id):
        self.id = id
        self.evet_dict[id] = "STOP"
        self.lock = Lock()

    def is_set(self):
        with self.lock:
            if self.evet_dict[self.id] in ["RUNNING", "WAIT"]:
                return True
            else:
                return False

    def start(self):
        with self.lock:
            self.evet_dict[self.id] = "RUNNING"

    def wait(self):
        with self.lock:
            self.evet_dict[self.id] = "WAIT"

    def stop(self):
        with self.lock:
            self.evet_dict[self.id] = "STOP"

    @property
    def state(self):
        with self.lock:
            return self.evet_dict[self.id]

    def __str__(self):
        with self.lock:
            return f"Event {self.id} is {self.state}"
