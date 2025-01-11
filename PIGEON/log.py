# 为中间层写一个日志系统
from datetime import datetime, timedelta
import os
import inspect


class inspect_infomation:
    @staticmethod
    def get_more_info():
        # 获取调用栈
        stack = inspect.stack()
        # 获取帧信息
        pre_frame = stack[2]
        # 获取调用信息
        code = pre_frame.frame.f_code
        function_name = code.co_name  # 当前函数名
        file_name = code.co_filename.split("\\")[-1]  # 当前文件名
        line_number = pre_frame.lineno  # 当前行号

        return file_name, function_name, line_number


class Log:
    log_emit = None
    last_log = None

    def __init__(self):
        Log_to_file.rename_file_if_older_than_one_day("log/log.txt")
        pass

    def info_nof(self, message):
        self.handler(message, "INFO")

    def info(self, message):
        self.handler(message, "INFO")
        Log_to_file.logtToFile(message, more_info=inspect_infomation.get_more_info(), level="INFO")

    def error(self, message):
        self.handler(message, "ERROR")
        Log_to_file.logtToFile(message, more_info=inspect_infomation.get_more_info(), level="ERROR")

    def debug(self, message):
        self.handler(message, "DEBUG")
        Log_to_file.logtToFile(message, more_info=inspect_infomation.get_more_info(), level="DEBUG")

    def warning(self, message):
        self.handler(message, "WARNING")
        Log_to_file.logtToFile(message, more_info=inspect_infomation.get_more_info(), level="WARNING")

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
                msg = {"time": f"{now} ", "content_info": f"{message}\n"}  # "tag":"content"
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
        if self.log_emit is None:
            print(f"{msg}")
            return
        if msg and cursor:
            line_text = self.log_emit.get(f"{line}.0", f"{line+1}.0")
            re_index = line_text.find("\n")
            if re_index == -1:  # 空行
                self.log_emit.insert(f"{line}.0", f"\n", tags=tags)  # 插入换行符
            else:  # 非空行 # 先删除该行，再插入
                self.log_emit.delete(f"{line}.0", f"{line}.{re_index}")  # 不删除换行符，避免影响光标位置
            self.log_emit.insert(f"{line}.{column}", f"{msg}", tags=tags)  # 插入日志信息
            self.log_emit.yview_moveto(0)
        Log_to_file.logtToFile(msg, more_info=inspect_infomation.get_more_info())

    def clear(self):
        self.log_emit.delete("1.0", "end")  # 清空日志信息

    def file(self, message):
        Log_to_file.logtToFile(message, more_info=inspect_infomation.get_more_info())


class Log_to_file:
    is_open = True
    last_log_message = None
    repeat_message = []
    max_size = 5

    @classmethod
    def _fmt(cls, message, more_info: tuple = None, level: str = "INFO"):
        # 获取当前时间
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 格式化日志信息
        message = message.replace("\n", " ")  # 去掉换行符
        if not cls.last_log_message:
            cls.write_to_file(f"\n{"━"*60}{now}{'━'*60}\n")
            cls.last_log_message = message
        elif message == cls.last_log_message:
            return None
        else:
            cls.last_log_message = message

        # 格式化日志信息
        msg = f">{now}|{level:>5}|{more_info[0]:>15}:{more_info[2]:<3}|{more_info[1][:20]:^20}||{message}\n"
        return msg

    @classmethod
    def filter_repeat_message(cls, message):
        """
        过滤重复日志信息
        :param message: 日志信息
        :return: 0 表示重复消息不输出;1 表示非重复消息,需要输出;-1表示不仅需要输出当前消息,还需要输出之前的重复消息并且清空集合
        """
        if len(cls.repeat_message) < cls.max_size:
            if message not in cls.repeat_message:
                cls.repeat_message.append(message)  # 添加到列表末尾
                return 1  # 表示新消息
            else:
                return 0  # 表示是重复消息
        else:
            if message not in cls.repeat_message:
                # 需要输出当前消息和集合中的所有消息，并清空集合
                return -1
            else:
                # 消息在集合中，是重复消息
                return 0

    @classmethod
    def logtToFile(cls, message: str, more_info: tuple = None, level: str = "INFO"):
        match cls.filter_repeat_message(message):
            case 0:
                return
            case 1:
                if msg := cls._fmt(message, more_info, level):
                    cls.write_to_file(msg)
                else:
                    return
            case -1:
                # 输出之前的重复消息
                for msg in cls.repeat_message:
                    if _msg := cls._fmt(msg, more_info, level):
                        cls.write_to_file(_msg)
                # 输出当前消息
                if msg := cls._fmt(message, more_info, level):
                    cls.write_to_file(msg)
                # 清空集合
                cls.repeat_message.clear()

    @classmethod
    def write_to_file(cls, message: str):
        if cls.is_open:
            with open("log/log.txt", "r+", encoding="utf-8") as f:
                # 先读取之前已有的内容
                lines = f.readlines()
                f.seek(0)  # 将文件指针指向开头
                f.write(message)  # 写入日志信息
                f.writelines(lines)  # 将之前的内容重新写入文件
        else:
            pass
            # print(f"日志文件已关闭，无法写入日志：{message}")

    @staticmethod
    def rename_file_if_older_than_one_day(file_path):
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"This is a log file auto created by PIGEON at {datetime.now()}\n")
            return
        # 获取文件的创建时间
        creation_time = os.path.getmtime(file_path)
        creation_date = datetime.fromtimestamp(creation_time)

        # 获取当前时间
        current_time = datetime.now().date()
        six_am_today = datetime.combine(current_time, datetime.strptime("06:00:00", "%H:%M:%S").time())

        # 计算文件创建时间是否于今日凌晨6点之前更改
        # print(f"文件创建时间：{creation_date}，当前时间：{current_time}，6点前：{six_am_today}")
        if creation_date < six_am_today and datetime.now() > six_am_today:
            # 生成新的文件名
            new_file_name = datetime.now().strftime("%Y-%m-%d %H-%M-%S") + ".txt"
            new_file_path = os.path.join(os.path.dirname(file_path), new_file_name).replace("\\", "/")

            # 重命名文件
            os.rename(file_path, new_file_path)


log = Log()
