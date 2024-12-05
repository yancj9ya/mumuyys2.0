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
                        self.emit(fmt_msg, tag="info")  # 输出日志信息
                else:
                    return
            case "ERROR":
                if msg := self.filiter(message):  # 过滤日志信息
                    fmt_msg = self.format(msg, level)  # 格式化日志信息
                    if fmt_msg:
                        self.emit(fmt_msg, tag="error")  # 输出日志信息
            case "DEBUG":
                if msg := self.filiter(message):  # 过滤日志信息
                    fmt_msg = self.format(msg, level)  # 格式化日志信息
                    if fmt_msg:
                        self.emit(fmt_msg, tag="debug")  # 输出日志信息
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
        match level:
            case "INFO":
                msg = {"time": f"| {now} | ", "content_info": f"{message}\n"}  # "tag":"content"
            case "ERROR":
                msg = {"time": f"| {now} | ", "content_error": f"{message}\n"}  # "tag":"content"
            case "DEBUG":
                msg = {"time": f"| {now} | ", "content_debug": f"{message}\n"}  # "tag":"content"
        return msg

    def emit(self, message, tag=None):
        # 输出日志信息
        if self.log_emit:
            index = 0
            for _tag, content in message.items():
                self.log_emit.insert(f"7.{index}", f"{content}", tags=_tag)
                index = len(content)
            self.log_emit.yview_moveto(0)
        else:
            print(message)

    def insert(self, cursor="end", msg="default message", tags="board"):
        # 获取当前时间
        # now = datetime.now().strftime("%H:%M:%S")
        line, column = int(cursor.split(".")[0]), int(cursor.split(".")[1])
        # 格式化日志信息
        if msg and cursor:
            line_text = self.log_emit.get(f"{line}.0", f"{line+1}.0")
            re_index = line_text.find("\n")
            if re_index == -1:  # 空行
                self.log_emit.insert(f"{line}.0", f"\n", tags=tags)  # 插入换行符
            else:  # 非空行 # 先删除该行，再插入
                self.log_emit.delete(f"{line}.0", f"{line}.{re_index}")  # 不删除换行符，避免影响光标位置
            self.log_emit.insert(f"{line}.{column}", f"{msg}", tags=tags)  # 插入日志信息
            self.log_emit.yview_moveto(0)

    def clear(self):
        self.log_emit.delete("1.0", "end")  # 清空日志信息


log = Log()
