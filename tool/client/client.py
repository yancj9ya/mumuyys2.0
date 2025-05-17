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
            buttons=[
                "确认",
                "取消",
            ],
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
    notification_thread.join(timeout + 2)
    timer.cancel()  # 如果提前完成则取消计时器

    return status.selected


if __name__ == "__main__":
    result = interactive_notification(timeout=5, default_choice="确认")
    print(f"最终选择：{result}")
