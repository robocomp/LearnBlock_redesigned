import math

from PySide2.QtCore import Signal


class Point(object):

    changed = Signal()

    def __init__(self, _x=0, _y=0):
        self.__x = _x
        self.__y = _y

    def __str__(self):
        return "Point(%s, %s)" % (self.__x, self.__y)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, other: float):
        return Point(int(self.x * other), (int(self.y * other)))

    @classmethod
    def from_dict(cls, datadict):
        return cls(datadict['_Point__x'], datadict['_Point__y'])

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, _x):
        self.__x = _x
        # self.changed.emit()

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, _y):
        self.__y = _y
        self.changed.emit()

    def move(self, _x, _y):
        self.__x += _x
        self.__y += _y
        # self.changed.emit()

    def set(self, _x, _y):
        self.__x = _x
        self.__y = _y
        # self.changed.emit()

    def distance(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx ** 2 + dy ** 2)


if __name__ == '__main__':
    for x in range(100):
        p = Point(0, x)
        print(p.__dict__)
        print(Point.fromdict(p.__dict__))
