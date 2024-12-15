# 创建一个图形类，以及一个节点数据类
# 节点由：1、节点本身包含可以被识别，2、节点的可跳转节点，以及对应的跳转方法 3、节点的属性


class node:
    def __init__(self, path, area, name):
        self.name = name
        self.path = path
        self.area = area
        self.edges = {}

    def add_edge(self, node, method):
        self.edges[node] = method
