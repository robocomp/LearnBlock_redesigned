import copy
import cv2

import os

import numpy as np
from PIL import ImageDraw
from PySide2.QtCore import Signal, QObject

from learnblock import textfont
from learnblock.utils import CV2ImagetoPILImage, PILImagetoCV2Image
from learnblock.utils.Types import BlockImgType, BlockType


def BlockPathtoConfigPath(_imgPath):
    confPath = os.path.splitext(_imgPath)[0].replace("desings", "configs")
    return confPath


def ConfigPathtoBlockPath(_confPath):
    _imgPath = _confPath.replace("configs", "desings") + ".png"
    return _imgPath


class Block:

    imgchanged = Signal()
    next_id = 0

    def __init__(self, _img, _text1: str, _text2: str, _vars: list, _type: BlockType, _typeIMG: BlockImgType, _id: int = None):
        self._img = _img
        self._showImg = _img
        self._text1 = _text1
        self._text2 = _text2
        self._vars = _vars
        self._type = _type
        self._typeIMG = _typeIMG
        self._blockSize = 34
        if _id is None:
            self._id = Block.next_id
            Block.next_id += 1
        else:
            self._id = _id
        self._hover = False

    @property
    def hover(self):
        return self._hover

    @hover.setter
    def hover(self, hover):
        self._hover = hover
        self.renderImgBlock()

    @property
    def img(self):
        return self._showImg

    @img.setter
    def img(self, _img):
        self._img = _img
        self.renderImgBlock()

    @property
    def block_size(self):
        return self._blockSize

    @block_size.setter
    def block_size(self, _blockSize):
        if self._blockSize != _blockSize:
            self._blockSize = _blockSize
            self.renderImgBlock()

    @property
    def text1(self):
        return self._text1

    @text1.setter
    def text1(self, _text1):
        self._text1 = _text1
        self.renderImgBlock()

    @property
    def text2(self):
        return self._text2

    @text2.setter
    def text2(self, _text2):
        self._text2 = _text2
        self.renderImgBlock()

    @property
    def vars(self):
        return self._vars

    @vars.setter
    def vars(self, _vars):
        self._vars = _vars
        self.renderImgBlock()

    @property
    def id(self):
        return self._id

    def renderImgBlock(self):
        img = copy.copy(self._img)
        varText = ""
        if BlockType.isfunction(self._type) or \
                (self._type is BlockType.CONTROL and len(self.vars) is not 0):
            varText = "(" + ", ".join(self.vars) + ")"
        elif self._type is BlockType.VARIABLE:
            for var in self.vars:
                varText = str(var)
                break

        text1 = self.text1 + varText
        text1Size = textfont.getsize(text1)[0]
        text2Size = textfont.getsize(self.text2)[0]
        textSize = max([text1Size, text2Size])

        if self._typeIMG is BlockImgType.COMPLEXBLOCK:

            left = img[0:img.shape[0], 0:60]
            right = img[0:img.shape[0], img.shape[1] - 10:img.shape[1]]
            line = img[0:img.shape[0], 72:73]

            h = left.shape[0]
            w = left.shape[1] + right.shape[1] + textSize

            im = np.ones((h, w, 4), dtype=np.uint8)
            im[0:h, 0:left.shape[1]] = copy.copy(left)
            im[0:right.shape[0], im.shape[1] - right.shape[1]:im.shape[1]] = copy.copy(right)
            for i in range(left.shape[1], im.shape[1] - right.shape[1]):
                im[0:line.shape[0], i:i + 1] = copy.copy(line)

            header = copy.copy(im[0:39, 0:im.shape[1]])
            foot = copy.copy(im[69:104, 0:im.shape[1]])
            line = copy.copy(im[50:51, 0:im.shape[1]])

            # blocks_in = self._blockSize

            h = header.shape[0] + foot.shape[0] + self._blockSize - 4
            w = header.shape[1]

            im = np.ones((h, w, 4), dtype=np.uint8)
            im[0:header.shape[0], 0:header.shape[1]] = header
            im[im.shape[0] - foot.shape[0]:im.shape[0], 0:foot.shape[1]] = foot
            for i in range(39, im.shape[0] - foot.shape[0]):
                im[i:i + line.shape[0], 0:header.shape[1]] = copy.copy(line[::, :header.shape[1]])
        else:
            left = img[0:img.shape[0], 0:43]
            right = img[0:img.shape[0], img.shape[1] - 10:img.shape[1]]
            line = img[0:img.shape[0], 43:44]

            h = left.shape[0]
            w = left.shape[1] + right.shape[1] + textSize

            im = np.ones((h, w, 4), dtype=np.uint8)
            im[0:left.shape[0], 0:left.shape[1]] = copy.copy(left)
            im[0:right.shape[0], im.shape[1] - right.shape[1]:im.shape[1]] = copy.copy(right)

            for i in range(left.shape[1], im.shape[1] - right.shape[1]):
                im[0:line.shape[0], i:i + 1] = copy.copy(line)

        im = self.updatehover(im)

        im = CV2ImagetoPILImage(im)
        draw = ImageDraw.Draw(im)

        draw.text(xy=(15, 3), text=text1, fill=(0, 0, 0, 255), font=textfont)
        draw.text((15, im.height - 35), self.text2, (0, 0, 0, 255), font=textfont)



        self._showImg = im

        self.imgchanged.emit()

    def updatehover(self, im):
        if self._hover:
            nS = 180
        else:
            nS = 0
        r, g, b, a = cv2.split(im)
        rgb = cv2.merge((r, g, b))
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        h, s, v = cv2.split(hsv)
        s = s + nS
        hsv = cv2.merge((h, s, v))
        im = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
        r, g, b = cv2.split(im)

        return cv2.merge((r, g, b, a))



if __name__ == '__main__':
    for x in range(100):
        b = Block()
        print(b.__dict__)
        print(Block.from_dict(b.__dict__))
