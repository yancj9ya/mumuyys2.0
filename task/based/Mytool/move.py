from base import windowControl
from bezier import BezierTrajectory
from random import randint,choices
from time import sleep
class Move(windowControl):
    def __init__(self,window_name):
        windowControl.__init__(self)
        self.handle=self.get_hwnd_by_name(window_name)
    
    def move_to(self, x: int, y: int):
        """移动鼠标到坐标（x, y)

        Args:
            handle (HWND): 窗口句柄
            x (int): 横坐标
            y (int): 纵坐标
        """
        wparam = 0
        lparam = y << 16 | x
        self.PostMessageW(self.handle, self.WM_MOUSEMOVE, wparam, lparam)
    @classmethod
    def get_bezier_params(cls, start_x: int, start_y: int, end_x: int, end_y: int):
        distance = ((end_x - start_x) ** 2 + (end_y - start_y) ** 2) ** 0.5
        bezier_num = int(distance//1)
        bezier_level = randint(1, 3)
        bezier_type = int(choices([1,2,3], weights=[0.1,0.6,0.1], k=1))
        return bezier_num, bezier_level ,bezier_type
        pass
    def move_by_bezier(self, start_x: int, start_y: int, end_x: int, end_y: int):
        bezier_num, bezier_level ,bezier_type = self.get_bezier_params(start_x, start_y, end_x, end_y)
        move_list = BezierTrajectory.trackArray(start=(start_x, start_y), end=(end_x, end_y), numberList=bezier_num, le=bezier_level,
                     deviation=10, bias=0.5, type=bezier_type,cbb=0, yhh=5)
        return move_list
        pass
    def move(self,start_x: int, start_y: int, end_x: int, end_y: int):
        move_list = self.move_by_bezier(start_x, start_y, end_x, end_y) 
        self.left_down(self.handle, start_x, start_y)
        for i in range(len(move_list)):
            self.move_to(move_list[i][0], move_list[i][1])
            sleep(0.8/len(move_list))
        self.left_up(self.handle, end_x, end_y)
        
if __name__ == '__main__':
    move = Move('阴阳师-网易游戏')
    move.move(442,484,456,164)   