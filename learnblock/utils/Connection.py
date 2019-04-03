from PySide2.QtCore import Signal, QObject

from learnblock.utils.Types import ConnectionType, BlockType
from learnblock.utils.point import Point


class Connection(object):
    """

    """
    changedConnection = Signal()

    def __init__(self, point: Point, parent, type: ConnectionType):
        # super(Connection, self).__init__()
        self.__parent = parent
        self.__point = point
        self.__type = type
        self.__connect = None
        self.__idConnected = None

    @classmethod
    def from_dict(cls, _dict):
        instance = cls(_dict["_Connection__point"], _dict["_Connection__parent"], _dict["_Connection__type"])
        instance.connect = _dict["_Connection__connect"]

    def __str__(self):
        return "Connection: \n" \
               "\tid parent : " + str(self.__parent.id()) + "\n" \
                "\tid item connected : " + str(self.__idConnected) + "\n" \
                "\ttype : " + str(self.__type) + "\n" \
                "\tposition = " + str(self.__point)

    @property
    def connect(self):
        return self.__connect, self.__idConnected

    @connect.setter
    def connect(self, other):

        if isinstance(other, Connection):
            self.__connect = other
            self.__idConnected = other.parent.id
        else:
            self.__connect = None
            self.__idConnected = None
        # self.changedConnection.emint()

    def connected(self):
        return self.__connect is not None

    def nextBottomConnect(self):
        if BlockType.BOTTOM in self.__parent.connections:
            return self.__parent.connections[BlockType.BOTTOM]
        return False

    @property
    def type(self):
        return self.__type

    @property
    def pos(self):
        pos =  self.__parent.pos()
        return self.__point + Point(pos.x(), pos.y())

    @property
    def point(self):
        return self.__point

    @point.setter
    def point(self, _point):
        self.__point = _point

    @property
    def parent(self):
        return self.__parent

    def __del__(self):
        del self.__parent
        del self.__connect
        del self.__point
        del self.__type
