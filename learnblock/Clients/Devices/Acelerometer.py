
class Acelerometer(object):
    '''
    Acelerometer is a class that contain the values rx, ry, rz of a Acelerometer in rad.
    '''

    def __init__(self, _readFunction):
        self._x = None
        self._y = None
        self._z = None
        self._readDevice = _readFunction

    def set(self, _x, _y, _z):
        self._x, self._y, self._z = _x, _y, _z

    def get(self):
        return self._x, self._y, self._z

    def read(self):
        _x, _y, _z = self._readDevice()
        self.set(_x, _y, _z)
