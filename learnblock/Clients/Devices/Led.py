from enum import Enum


class LedStatus(Enum):
    ON = True
    OFF = False


class Led(object):

    def __init__(self, _setState=None, _readState=None):
        self._State = None
        self._setState = _setState
        self._readState = _readState

    def read(self):
        if self._readState is not None:
            self._State = self._readState()

    @property
    def state(self):
        return self._State

    @state.setter
    def state(self, _status):
        self._setState(_status)
        _State = _status


class RGBLed(object):

    def __init__(self, _setColorState=None, _readState=None):
        self._State = None
        self._readState = _readState
        self._setColorState = _setColorState

    def read(self):
        if self._readState is not None:
            self._State = self._readState()

    @property
    def state(self):
        return self._State

    @state.setter
    def state(self, _rgb):
        _r, _g, _b = _rgb
        if self._setColorState is not None:
            self._setColorState(_r, _g, _b)
            self._State = _rgb
