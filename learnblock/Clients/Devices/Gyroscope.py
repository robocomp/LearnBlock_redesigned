
class Gyroscope(object):
    '''
    Gyroscope is a class that contain the values rx, ry, rz of a Gyroscope in rad.
    '''

    def __init__(self, _readFunction):
        self.rx = 0
        self.ry = 0
        self.rz = 0
        self.__readDevice = _readFunction

    def set(self, _rx, _ry, _rz):
        self.rx, self.ry, self.rz = _rx, _ry, _rz

    def get(self):
        return self.rx, self.ry, self.rz

    def read(self):
        _rx, _ry, _rz = self.__readDevice()
        self.set(_rx, _ry, _rz)
