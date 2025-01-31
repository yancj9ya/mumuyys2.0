from threading import Lock
from weakref import WeakKeyDictionary
from PIGEON.log import log


class _EventState:
    """Wrapper class for event states"""

    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if isinstance(other, _EventState):
            return self.value == other.value
        return self.value == other

    def __str__(self):
        return str(self.value)


class MyEvent:
    """Thread-safe event controller with automatic cleanup"""

    _event_dict = WeakKeyDictionary()
    _lock = Lock()
    _STATES = {"STOP": _EventState("STOP"), "RUNNING": _EventState("RUNNING"), "WAIT": _EventState("WAIT")}

    def __init__(self, event_id):
        self.id = event_id
        with self._lock:
            self._event_dict[self] = self._STATES["STOP"]

    def is_set(self):
        """Check if event is running or waiting"""
        return self.state in (self._STATES["RUNNING"], self._STATES["WAIT"])

    def start(self):
        """Set event to running state"""
        with self._lock:
            self._event_dict[self] = self._STATES["RUNNING"]

    def wait(self):
        """Set event to wait state"""
        with self._lock:
            self._event_dict[self] = self._STATES["WAIT"]

    def stop(self):
        """Set event to stop state"""
        with self._lock:
            self._event_dict[self] = self._STATES["STOP"]

    def clear(self):
        """Clear all events"""
        log.info(f"Clearing all events by {self.id}")
        with self._lock:
            for event in list(self._event_dict.keys()):
                if self._event_dict[event] in (self._STATES["RUNNING"], self._STATES["WAIT"]):
                    self._event_dict[event] = self._STATES["STOP"]

    @property
    def state(self):
        """Get current event state"""
        with self._lock:
            return self._event_dict[self]

    def __str__(self):
        """String representation of event state"""
        return f"Event {self.id} is {self.state}"

    def __del__(self):
        """Clean up event on deletion"""
        self.stop()
