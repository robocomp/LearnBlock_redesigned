import copy, numpy as np


class Camera(object):
    '''
    Camera devices.
    '''

    def __init__(self, _readFunction):
        self.__image = np.zeros((240, 320, 3), np.uint8)     # RGB image 240x320
        self.__newImageAvailable = False
        self._readDevice = _readFunction

    def read(self):
        img, new = self._readDevice()
        if new is True:
            self.__image = img
            self.__newImageAvailable = True
    @property
    def image(self):
        simage = copy.copy(self.__image)
        return simage

    @property
    def newAvailable(self):
        return self.__newImageAvailable

    def disableNewImageAvailable(self):
        self.__newImageAvailable = False
