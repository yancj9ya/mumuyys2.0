"""
author: cbb
这个库基于贝塞尔曲线实现模拟人手动滑动的轨迹
可以用于selenium轨迹的模拟，或者生成轨迹数组用于js加密通过网站服务器后端分控检测
QQ群 134064772
里面的人说话好听，个个都是人才
"""

import numpy as np


import math
import random


class BezierTrajectory:

    @classmethod
    def _bztsg(cls, dataTrajectory):
        lengthOfdata = len(dataTrajectory)

        def staer(x):
            t = (x - dataTrajectory[0][0]) / (dataTrajectory[-1][0] - dataTrajectory[0][0])
            y = np.array([0, 0], dtype=np.float64)
            for s in range(len(dataTrajectory)):
                y += dataTrajectory[s] * ((math.factorial(lengthOfdata - 1) / (math.factorial(s) * math.factorial(lengthOfdata - 1 - s))) * math.pow(t, s) * math.pow((1 - t), lengthOfdata - 1 - s))
            return y[1]

        return staer

    @classmethod
    def _type(cls, type, x, numberList):
        numberListre = []
        pin = (x[1] - x[0]) / numberList
        if type == 0:
            for i in range(numberList):
                numberListre.append(i * pin)
            if pin >= 0:
                numberListre = numberListre[::-1]
        elif type == 1:
            for i in range(numberList):
                numberListre.append(1 * ((i * pin) ** 2))
            numberListre = numberListre[::-1]
        elif type == 2:
            for i in range(numberList):
                numberListre.append(1 * ((i * pin - x[1]) ** 2))

        elif type == 3:
            dataTrajectory = [np.array([0, 0]), np.array([(x[1] - x[0]) * 0.8, (x[1] - x[0]) * 0.6]), np.array([x[1] - x[0], 0])]
            fun = cls._bztsg(dataTrajectory)
            numberListre = [0]
            for i in range(1, numberList):
                numberListre.append(fun(i * pin) + numberListre[-1])
            if pin >= 0:
                numberListre = numberListre[::-1]
        numberListre = np.abs(np.array(numberListre) - max(numberListre))
        biaoNumberList = ((numberListre - numberListre[numberListre.argmin()]) / (numberListre[numberListre.argmax()] - numberListre[numberListre.argmin()])) * (x[1] - x[0]) + x[0]
        biaoNumberList[0] = x[0]
        biaoNumberList[-1] = x[1]
        return biaoNumberList

    @classmethod
    def getFun(cls, s):
        """

        :param s: 传入P点
        :return: 返回公式
        """
        dataTrajectory = []
        for i in s:
            dataTrajectory.append(np.array(i))
        return cls._bztsg(dataTrajectory)

    @classmethod
    def simulation(cls, start, end, le=1, deviation=0, bias=0.5):
        """

        :param start:开始点的坐标 如 start = [0, 0]
        :param end:结束点的坐标 如 end = [100, 100]
        :param le:几阶贝塞尔曲线，越大越复杂 如 le = 4
        :param deviation:轨迹上下波动的范围 如 deviation = 10
        :param bias:波动范围的分布位置 如 bias = 0.5
        :return:返回一个字典equation对应该曲线的方程，P对应贝塞尔曲线的影响点
        """
        start = np.array(start)
        end = np.array(end)
        cbb = []
        if le != 1:
            e = (1 - bias) / (le - 1)
            cbb = [[bias + e * i, bias + e * (i + 1)] for i in range(le - 1)]

        dataTrajectoryList = [start]

        t = random.choice([-1, 1])
        w = 0
        for i in cbb:
            px1 = start[0] + (end[0] - start[0]) * (random.random() * (i[1] - i[0]) + (i[0]))
            p = np.array([px1, cls._bztsg([start, end])(px1) + t * deviation])
            dataTrajectoryList.append(p)
            w += 1
            if w >= 2:
                w = 0
                t = -1 * t

        dataTrajectoryList.append(end)
        return {"equation": cls._bztsg(dataTrajectoryList), "P": np.array(dataTrajectoryList)}

    @classmethod
    def trackArray(cls, start, end, numberList, le=1, deviation=0, bias=0.5, type=0, cbb=0, yhh=10):
        """

        :param start:开始点的坐标 如 start = [0, 0]
        :param end:结束点的坐标 如 end = [100, 100]
        :param numberList:返回的数组的轨迹点的数量 numberList = 150
        :param le:几阶贝塞尔曲线，越大越复杂 如 le = 4
        :param deviation:轨迹上下波动的范围 如 deviation = 10
        :param bias:波动范围的分布位置 如 bias = 0.5
        :param type:0表示均速滑动，1表示先慢后快，2表示先快后慢，3表示先慢中间快后慢 如 type = 1
        :param cbb:在终点来回摆动的次数
        :param yhh:在终点来回摆动的范围
        :return:返回一个字典trackArray对应轨迹数组，P对应贝塞尔曲线的影响点
        """
        s = []
        fun = cls.simulation(start, end, le, deviation, bias)
        w = fun["P"]
        fun = fun["equation"]
        if cbb != 0:
            numberListOfcbb = round(numberList * 0.2 / (cbb + 1))
            numberList -= numberListOfcbb * (cbb + 1)

            xTrackArray = cls._type(type, [start[0], end[0]], numberList)
            for i in xTrackArray:
                s.append([i, fun(i)])
            dq = yhh / cbb
            kg = 0
            ends = np.copy(end)
            for i in range(cbb):
                if kg == 0:
                    d = np.array([end[0] + (yhh - dq * i), ((end[1] - start[1]) / (end[0] - start[0])) * (end[0] + (yhh - dq * i)) + (end[1] - ((end[1] - start[1]) / (end[0] - start[0])) * end[0])])
                    kg = 1
                else:
                    d = np.array([end[0] - (yhh - dq * i), ((end[1] - start[1]) / (end[0] - start[0])) * (end[0] - (yhh - dq * i)) + (end[1] - ((end[1] - start[1]) / (end[0] - start[0])) * end[0])])
                    kg = 0
                print(d)
                y = cls.trackArray(ends, d, numberListOfcbb, le=2, deviation=0, bias=0.5, type=0, cbb=0, yhh=10)
                s += list(y["trackArray"])
                ends = d
            y = cls.trackArray(ends, end, numberListOfcbb, le=2, deviation=0, bias=0.5, type=0, cbb=0, yhh=10)
            s += list(y["trackArray"])

        else:
            xTrackArray = cls._type(type, [start[0], end[0]], numberList)
            for i in xTrackArray:
                s.append([i, fun(i)])
        # print(s)
        # return {"trackArray": np.array(s), "P": w}
        return [[int(s[0]), int(s[1])] for s in s if np.isnan(s[1]) == False and np.isinf(s[1]) == False]

    # print(BezierTrajectory.trackArray(start=[0, 0], end=[100, 100], numberList=50, le=2,deviation=0, bias=0.5, type=0, cbb=0, yhh=10))
    @classmethod
    def _get_bezier_params(cls, start_x: int, start_y: int, end_x: int, end_y: int):
        distance = ((end_x - start_x) ** 2 + (end_y - start_y) ** 2) ** 0.5
        bezier_num = int(abs(end_x - start_x) / 4) if abs(end_x - start_x) > abs(end_y - start_y) else int(abs(end_y - start_y) / 4)
        bezier_level = random.randint(1, 3)
        bezier_type = random.choices([1, 2, 3], weights=[0.1, 0.6, 0.1], k=1)
        return bezier_num, bezier_level, bezier_type
        pass

    @classmethod
    def move_by_bezier(cls, start_x: int, start_y: int, end_x: int, end_y: int):
        start_x += random.randint(-5, 5)
        start_y += random.randint(-5, 5)
        end_x += random.randint(-5, 5)
        end_y += random.randint(-5, 5)

        if start_x == end_x:
            end_x = start_x + 3
        if start_y == end_y:
            end_y = start_y + 3

        bezier_num, bezier_level, bezier_type = cls._get_bezier_params(start_x, start_y, end_x, end_y)
        # print(bezier_num, bezier_level, bezier_type)
        move_list = BezierTrajectory.trackArray(start=(start_x, start_y), end=(end_x, end_y), numberList=bezier_num, le=bezier_level, deviation=10, bias=0.5, type=bezier_type[0], cbb=0, yhh=5)

        if abs(end_x - start_x) >= abs(end_y - start_y):  # 横坐标差值大于纵坐标差值，则为横向移动
            print("横向移动")
            if start_x > end_x:  # 向右滑动
                return sorted(move_list, key=lambda x: x[0], reverse=True)
            else:  # 向左滑动
                return sorted(move_list, key=lambda x: x[0])
        else:  # 纵坐标差值大于横坐标差值，则为纵向移动
            print("纵向移动")
            if start_y > end_y:  # 向上滑动
                return sorted(move_list, key=lambda x: x[1], reverse=True)
            else:  # 向下滑动
                return sorted(move_list, key=lambda x: x[1])
        pass


if __name__ == "__main__":
    # (1168, 172, 1202, 207), (1161, 466, 1193, 517)
    start, end = [1162, 146, 1226, 203], [231, 133, 301, 199]
    s_x, s_y = random.randint(start[0], start[2]), random.randint(start[1], start[3])
    e_x, e_y = random.randint(end[0], end[2]), random.randint(end[1], end[3])
    print(s_x, s_y, e_x, e_y)
    print(BezierTrajectory.move_by_bezier(s_x, s_y, e_x, e_y))
