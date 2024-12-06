from task.based.Mytool.windows import Windows
from task.based.Mytool.Somenewidea import newidea
from task.based.Mytool.bezier import BezierTrajectory

# from task.based.Mytool.random_coord import BezierTrajectory
from task.based.Mytool.random_coord import RandomCoord
from time import sleep
from random import randint
from ctypes import windll

windll.user32.SetProcessDPIAware()


class Click(Windows):

    def __init__(self):
        super().__init__()

    def click(self, x, y, press_time=0.2, animation_time=0.05) -> None:
        x, y = int(x), int(y)  # 缩放坐标
        # self.notifyparent(x, y)#通知父类
        # self.mouseactivate()
        # self.setcursor()
        self.left_down(x, y)
        sleep(press_time)
        self.left_up(x, y)
        sleep(animation_time)
        # self.setcursor()
        # self.mouse_move(x, y)

    def area_click(self, area: list | tuple, press_time=0.2, double_click=False, double_click_time=0.1, animation_time=0.05) -> None:
        # rand_x = randint(area[0], area[2])
        # rand_y = randint(area[1], area[3])
        rand_x, rand_y = RandomCoord(area)
        if double_click:
            self.click(rand_x, rand_y, press_time, animation_time)
            sleep(double_click_time)
            self.click(rand_x, rand_y, press_time, animation_time)
        else:
            self.click(rand_x, rand_y, press_time, animation_time)

    def mouse_scroll(self, d_t: tuple[str, int], x: int, y: int) -> None:
        rect = self.get_window_rect()
        x += rect[0]
        y += rect[1]
        match d_t[0]:
            case "up":
                for i in range(d_t[1]):
                    self.wheel_scroll(120, x, y)
                    sleep(0.1)
            case "down":
                for i in range(d_t[1]):
                    self.wheel_scroll(-120, x, y)
                    sleep(0.1)

    def slide(self, start: list | tuple, end: list | tuple, move_time=0.5) -> None:
        # 如果长度为4则是rect，获取rect内的随机点坐标，以元组返回
        if len(start) == 4:
            start = newidea.rect_random_point(start)
            end = newidea.rect_random_point(end)
        # 获取贝塞尔曲线
        move_list = BezierTrajectory.move_by_bezier(*start, *end)
        # print(len(move_list),move_list,start,end)
        # 计算每一步的时间间隔
        slide_delay = move_time / len(move_list)
        # 开始滑动
        self.left_down(*start)
        for point in move_list:
            self.mouse_move(*point)
            sleep(slide_delay)
        self.left_up(*end)
        pass
