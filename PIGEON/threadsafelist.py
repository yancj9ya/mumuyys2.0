# This file is used to create a thread-safe list.

import threading


class ThreadSafeList:
    def __init__(self):
        self._list = []  # 普通列表
        self._lock = threading.Lock()  # 线程锁

    def append(self, item):
        with self._lock:  # 加锁，确保线程安全
            self._list.append(item)

    def remove(self, item):
        with self._lock:
            self._list.remove(item)

    def get(self, index):
        with self._lock:
            return self._list[index]

    def __len__(self):
        with self._lock:
            return len(self._list)

    def to_list(self):  # 返回一个线程安全的浅拷贝
        with self._lock:
            return list(self._list)

    def __iter__(self):
        # 获取列表的快照（浅拷贝）用于迭代，确保迭代时线程安全
        with self._lock:
            snapshot = list(self._list)
        # 返回快照的迭代器
        return iter(snapshot)

    def pop(self, index=-1):
        with self._lock:
            if len(self._list) == 0:
                raise IndexError("pop from empty list")
            return self._list.pop(index)

    def __contains__(self, item):
        with self._lock:
            return item in self._list
