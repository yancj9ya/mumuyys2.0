# 为中间层写一个日志系统
from datetime import datetime, date, time


class Log:
    log_emit = None
    last_log = None

    def __init__(self):
        pass

    def info(self, message):
        self.handler(message, "INFO")

    def error(self, message):
        self.handler(message, "ERROR")

    def debug(self, message):
        self.handler(message, "DEBUG")

    def warning(self, message):
        self.handler(message, "WARNING")

    def handler(self, message, level):
        match level:
            case "INFO":
                if msg := self.filiter(message):  # 过滤日志信息
                    fmt_msg = self.format(msg, level)  # 格式化日志信息
                    if fmt_msg:
                        self.emit(fmt_msg)  # 输出日志信息

                else:
                    return
            case _:
                pass

    def filiter(self, message):
        if self.last_log == message:
            return None
        else:
            self.last_log = message  # 更新上一次日志信息
        # 过滤日志信息
        return message

    def format(self, message, level):
        # 获取当前时间
        now = datetime.now().strftime("%H:%M:%S")
        # 格式化日志信息

        return f"[{now}]:{message}"

    def emit(self, message):
        # 输出日志信息
        if self.log_emit:
            # self.log_emit.yview_moveto(1)
            self.log_emit.insert("7.0", message + "\n", tags="green_text")
            self.log_emit.yview_moveto(0)
        else:
            print(message)

    def insert(self, cursor="end", msg="default message", tags=None):
        # 获取当前时间
        # now = datetime.now().strftime("%H:%M:%S")
        line, column = int(cursor.split(".")[0]), int(cursor.split(".")[1])
        # 格式化日志信息
        if msg and cursor:
            if self.log_emit.get(f"{line}.0", f"{line+1}.0") == "":  # 判断是空行
                self.log_emit.insert(f"{line}.0", f"\n", tags=tags)  # 插入换行符
            else:  # 非空行 # 先删除该行，再插入
                self.log_emit.delete(f"{line}.0", f"{line+1}.0")
                self.log_emit.insert(f"{line}.0", f"\n", tags=tags)  # 插入换行符
            self.log_emit.insert(f"{line}.{column}", f"{msg}", tags=tags)  # 插入日志信息
            self.log_emit.yview_moveto(0)

    def clear(self):
        self.log_emit.delete("1.0", "end")  # 清空日志信息


log = Log()
