# 一些新的想法实现
from random import randint
from PIGEON.log import Log

log = Log()


class rect:
    def __init__(self) -> None:
        pass

    pass


class newidea:
    screen_width = 1280
    screen_height = 720

    # 从矩形区域返回矩形区域内随机的点坐标
    @classmethod
    def rect_random_point(cls, rect: list | tuple) -> tuple:
        s_x, s_y, e_x, e_y = cls._identy_rect(rect)
        return (randint(s_x, e_x - 1), randint(s_y, e_y - 1))
        pass

    # 矩形区域不能超过屏幕的范围，如果超过则缩减到屏幕范围
    @classmethod
    def _identy_rect(cls, rect: list | tuple):
        s_x, s_y, e_x, e_y = rect
        try:
            assert s_x < e_x and s_y < e_y, "invalid rect"
            assert s_x >= 0 and s_y >= 0 and e_x <= cls.screen_width and e_y <= cls.screen_height, "rect out of screen"
        except AssertionError as e:
            log.error(e)
        return (max(s_x, 0), max(s_y, 0), min(e_x, cls.screen_width), min(e_y, cls.screen_height))
        pass
