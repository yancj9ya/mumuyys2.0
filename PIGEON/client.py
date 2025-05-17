# 用于启动客户端程序

import subprocess
from tool.Mytool.imageRec import ImageRec
from PIGEON.log import log
from json import loads
from win11toast import toast
import threading


def interactive_notification(timeout=15, default_choice="默认选项"):
    # 定义用户选择状态存储对象
    class ChoiceStatus:
        selected = None

    # 超时处理函数
    def timeout_handler(status):
        if status.selected is None:
            status.selected = default_choice
            print(f"超时未选择，自动执行：{default_choice}")

    # 显示通知并等待选择
    def show_notification(status):
        response = toast(
            title="是否关闭客户端",
            body="请在5秒内做出选择",
            buttons=["confirm", "cancel"],
            on_click=lambda args: setattr(status, "selected", args.get("arguments").split(":")[-1]),
        )
        # 处理无按钮点击的情况
        if status.selected is None and not response:
            status.selected = default_choice

    status = ChoiceStatus()

    # 启动通知线程
    notification_thread = threading.Thread(target=show_notification, args=(status,))
    notification_thread.start()

    # 设置超时计时器
    timer = threading.Timer(timeout, timeout_handler, args=(status,))
    timer.start()

    # 等待结果
    notification_thread.join(timeout + 1)
    timer.cancel()  # 如果提前完成则取消计时器

    return status.selected


class Client:
    def __init__(self):
        self.is_client_start_by_script = False
        self.need_ask_for_close_client = False
        self.imgrec = ImageRec()
        self.Manager_path = r"H:\MuMu Player 12\shell\MuMuManager.exe"

    def execute_cmd(self, cmd):
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                encoding="utf-8",
            )
            return loads(result.stdout) if result.returncode == 0 else None
        except subprocess.CalledProcessError as e:
            log.error(f"execute_cmd error {e}")
            return None
        except Exception as e:
            log.error(f"未知错误: {e}")
            return None

    def start_client_and_game(self, only_game=False):
        """启动客户端并进入游戏"""
        if only_game:
            mode = "launch app"
        else:
            mode = "launch"
            self.is_client_start_by_script = True
            self.need_ask_for_close_client = True

        cmd = [self.Manager_path, "control", "-v", "0", mode, "-pkg", "com.netease.onmyoji.wyzymnqsd_cps"]
        return self.execute_cmd(cmd)

    def get_client_info(self):
        cmd = [self.Manager_path, "info", "-v", "0"]
        return self.execute_cmd(cmd)

    def is_app_started(self):
        """检查应用是否已启动"""
        res = self.get_client_info()
        if res is None:
            return False
        status = res.get("player_state", None)
        # log.info(f"{status=}")
        return status == "start_finished"

    def client_stop(self):
        """关闭客户端"""
        if not self.is_client_start_by_script or not self.need_ask_for_close_client:
            return
        else:
            result = interactive_notification(timeout=5, default_choice="确认")
            if result == "confirm":
                cmd = [self.Manager_path, "control", "-v", "0", "shutdown"]
                return self.execute_cmd(cmd)
            else:
                self.need_ask_for_close_client = False
                return None

    def get_game_status(self):
        """获取游戏状态"""
        cmd = [self.Manager_path, "control", "-v", "0", "app", "info", "-pkg", "com.netease.onmyoji.wyzymnqsd_cps"]
        result = self.execute_cmd(cmd)
        if result:
            game_state = result.get("state", None)
            log.info(f"{game_state=}")
        return game_state

    def is_game_start(self):
        """检查游戏是否已启动"""
        state = self.get_game_status()
        return state == "running"

    def verify_app_and_game_start_finish(self):
        """检查游戏UI是否已准备好"""
        app_server = ["PIGEON/config/app_server.bmp", (11, 465, 256, 678), "app_server"]
        res = self.imgrec.match_img(app_server, accuracy=0.75)
        if res:
            log.info(f"app_server found {res}, 客户端启动完成")
            return True
        else:
            self.imgrec.win.del_cache()
            return False


if __name__ == "__main__":
    result = interactive_notification(timeout=5, default_choice="确认")
    print(f"最终选择：{result}")
