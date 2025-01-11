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

    def to_list(self):  # 返回一个线程安全的浅拷贝
        with self._lock:
            return list(self._list)

    def to_list(self):  # 返回一个线程安全的浅拷贝
        with self._lock:
            return list(self._list)

    def pop(self, index=-1):
        with self._lock:
            if len(self._list) == 0:
                raise IndexError("pop from empty list")
            return self._list.pop(index)

    def __iter__(self):
        # 获取列表的快照（浅拷贝）用于迭代，确保迭代时线程安全
        with self._lock:
            snapshot = list(self._list)
        # 返回快照的迭代器
        return iter(snapshot)

    def __contains__(self, item):
        with self._lock:
            return item in self._list

    def __len__(self):
        with self._lock:
            return len(self._list)

    def __add__(self, other):
        with self._lock:
            if isinstance(other, ThreadSafeList):
                # 返回一个新的 ThreadSafeList 对象，合并当前列表和另一个线程安全列表
                new_list = ThreadSafeList()
                new_list._list = self._list + other.to_list()
                return new_list
            elif isinstance(other, list):
                # 如果是普通列表，直接合并
                new_list = ThreadSafeList()
                new_list._list = self._list + other
                return new_list
            else:
                raise TypeError("Unsupported type for addition")
