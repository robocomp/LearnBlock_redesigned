
class Base(object):

    """
    Base is the differential base of the robot.
    """


    def __init__(self, _callFunction):
        self.__Sadv = 0  # in mm/s
        self.__Srot = 0  # in rad/s
        self.__callDevice = _callFunction

    def move(self, _Sadv, _Srot):
        self.__Sadv, self.__Srot = _Sadv, _Srot
        self.__callDevice(_Sadv, _Srot)

    @property
    def adv(self):
        return self.__Sadv

    @property
    def rot(self):
        return self.__Srot
