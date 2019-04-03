import copy

import cv2
import json
import os
import tempfile

from PySide2.QtCore import QSize
from PySide2.QtGui import QPaintEvent, QIcon
from PySide2.QtWidgets import QPushButton

from learnblock.scr.QGraphicsBlockItem import QGraphicsBlockItem
from learnblock.utils.Block import Block, ConfigPathtoBlockPath
from learnblock.utils.Connection import Connection
from learnblock.utils.Language import Language
from learnblock.utils.Types import BlockType, VariableType, BlockImgType, ConnectionType, Colors
from learnblock.utils.Variable import Variable
from learnblock.utils.point import Point
from learnblock.utils.Translations import Translations


def str2hex(tmpFile):
    return tmpFile.encode('utf-8').hex()


class ButtonBlock(QPushButton, Block):

    def __init__(self, _parent, _table, _row: int, _imgfileconf: str, _functionmame: str,
                 _translations: dict,
                 _tooltips: dict, _vars: list,
                 _type: BlockType):
        self._parent = _parent
        self._table = _table
        self._row = _row
        self._Variables = []
        self._translations = Translations(_translations)
        self._tooltips = Translations(_tooltips)
        self._functionmame = _functionmame
        self._connections = {}
        self._imgfileconf = _imgfileconf
        self._imgfile = ConfigPathtoBlockPath(self._imgfileconf)
        self._typeImg = BlockImgType.SIMPLEBLOCK  # by default
        self._type = _type
        self._language = Language()

        _varstext = self.initVars(_vars=_vars)
        self.initConections()

        self._initIMG()

        QPushButton.__init__(self, _parent)
        Block.__init__(self, _img=self._img, _text1="", _text2="", _vars=_varstext, _type=self._type,
                       _typeIMG=self._typeImg)

        self._language.changed.connect(self.changeLanguage)
        self.imgchanged.connect(self.updateImgButton)
        self._parent.ui.splitter.splitterMoved.connect(self.updateIconSize)
        self.clicked.connect(self.on_clickedButton)

    def changeLanguage(self):
        _varstext = []
        for v in self._Variables:
            _varstext.append(v.getName())
        self.vars =_varstext
        # self._initTranslations()
        self.text1 = self._translations[self._language.language]
        # self._tooltips.setdefault(self._language.language, "")
        textTooltip = self.text1 + ": " + self._tooltips[self._language.language]
        textout = ""
        sizeline = 0
        for word in textTooltip.split(" "):
            sizeline += len(word)
            if sizeline < 50:
                textout += word + " "
            else:
                textout += "\n" + word + " "
                sizeline = len(word)
        self.setToolTip(textout)

    def initConections(self):
        with open(self._imgfileconf, "r") as f:
            conf = json.load(f)
            self._typeImg = BlockImgType.fromString(conf["type"])
            self._connections_conf = conf
            for p in conf["points"]:
                _type = ConnectionType.fromString(p["type"])
                self._connections[_type] = Connection(Point(p["x"], p["y"]), self, _type)

    def _initTranslations(self):
        if self._language.language.upper() not in self._translations.keys():
            if self._language.language.lower() != "en":
                    self._translations.setdefault(self._language.language.upper(), self._functionmame)
            else:
                self._translations.setdefault(self._language.language.upper(), self._functionmame)

    def _initIMG(self):
        t = [k._name_ for k in self._connections.keys()]
        # self._initTranslations()
        # tmpFile = self._translations[self._language.language] + str(self._type) + str(self._typeImg) + str(
        #     len(self._connections)) + "".join(t)
        self.color = Colors.fromBlockType(self._type)
        tmpFile = self.color._name_ + self._imgfileconf
        self.tmpFile = os.path.join(tempfile.gettempdir(), "." + str2hex(tmpFile) + ".png")
        if not os.path.exists(self.tmpFile):
            im = cv2.imread(self._imgfile, cv2.IMREAD_UNCHANGED)
            r, g, b, a = cv2.split(im)
            rgb = cv2.merge((r, g, b))
            hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
            h, s, v = cv2.split(hsv)
            h = h + self.color.value
            s = s + 130
            hsv = cv2.merge((h, s, v))
            im = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
            r, g, b = cv2.split(im)
            self._img = cv2.merge((r, g, b, a))
            # self.updateIMGBlock()

            cv2.imwrite(self.tmpFile, self._img, (cv2.IMWRITE_PNG_COMPRESSION, 9))
        else:
            self._img = cv2.imread(self.tmpFile, cv2.IMREAD_UNCHANGED)
        self._showImg = self._img.copy()

    def initVars(self, _vars):
        _varstext = []
        for v in _vars:
            value = VariableType.getValue(v["type"], v["default"])
            v.setdefault("translate", {"EN": v["name"]})
            variableInstance = Variable(v["type"], name=v["name"], default=value, translate=Translations(v["translate"]))
            self._Variables.append(variableInstance)
            _varstext.append(variableInstance.getName())
        return _varstext

    def updateIconSize(self):
        width = self._parent.ui.functions.width() - 51
        size = self.iconSize()
        size.setWidth(width)
        size.setHeight(self._table.rowHeight(self._row))
        self.setIconSize(size)

    def updateImgButton(self):
        # cv2.imwrite(self.tmpFile, self.img, (cv2.IMWRITE_PNG_COMPRESSION, 9))
        icon = QIcon()
        icon.addPixmap(self.img.toqpixmap())
        width = self._parent.ui.functions.width() - 51
        self._table.setColumnWidth(0, width - 20)
        size = QSize(width - 20, self.img.height)
        self.setIconSize(size)
        self._table.setRowHeight(self._row, self.img.height)
        self.setIcon(icon)
        # self.setIcon(QIcon(self.tmpFile))
        self.setStyleSheet("QPushButton { text-align: left; }")

    def on_clickedButton(self):
        scene = self._parent.scene
        item = QGraphicsBlockItem(_parent=self, _imgfile=self.tmpFile, _functionname=self._functionmame,
                                  _translations=self._translations, _vars=copy.copy(self._Variables),
                                  _connections=self._connections_conf, _type=self._type,
                                  _typeIMG=self._typeImg)
        scene.addItem(item)
