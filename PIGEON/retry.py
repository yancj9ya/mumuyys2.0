import time
import functools


def retry(max_retries=3, delay=1, exceptions=(Exception,), on_retry=None):
    """
    重试装饰器，支持回调函数
    :param max_retries: 最大重试次数
    :param delay: 每次重试的延迟时间
    :param exceptions: 捕获的异常类型
    :param on_retry: 重试时的回调函数，可以是日志记录、状态更新等
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if on_retry:
                        on_retry(retries, e)  # 执行回调函数
                    print(f"Attempt {retries} failed: {e}. Retrying in {delay} seconds...")
                    if retries < max_retries:
                        time.sleep(delay * retries)  # 延时再试
                    else:
                        print("Max retries reached, raising exception.")
                        raise e

        return wrapper

    return decorator
