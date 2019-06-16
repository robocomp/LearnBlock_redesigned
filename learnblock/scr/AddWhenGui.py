from __future__ import print_function, absolute_import
import os
import cv2
from PIL import Image
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QDialog
from singleton_decorator import singleton

from learnblock import Language, PATHBLOCKSIMG, PATHBLOCKSCONF
from learnblock.guis import AddWhen
from learnblock.utils import PILImagetoCV2Image
from learnblock.utils.Block import Block
from learnblock.utils.Translations import Translations
from learnblock.utils.Types import Colors, BlockType, BlockImgType

listBlock = []
listNameBlocks = []


for base, dirs, files in os.walk(PATHBLOCKSIMG):
    for f in files:
        archivo, extension = os.path.splitext(base + "/" + f)
        if extension == ".png" and "block" in f and "azul" not in f:
            if "block8" in f or "block10" in f:
                listBlock.append(base + "/" + f)
                archivo, extension = os.path.splitext(f)
                listNameBlocks.append(archivo)

def nameBlocToConfigBlock(name):
    return os.path.join(PATHBLOCKSCONF, name)

listTypeBlock = ["control",
                 "motor",
                 "perceptive",
                 "propioperceptive",
                 "operator"]

listconfig = ["configControl",
              "configMotor",
              "configOperators",
              "configPerceptual"
              "configPropriopercetive"]


class AddWhenGui(QDialog):

    def __init__(self):
        QDialog.__init__(self)
        self.blockType = None
        self._translations = Translations(seq={'EN':"when", 'ES': "Cuando"})
        self.nameControl = ""
        self.FuntionType = None
        self.img = None
        self.imgName = []
        self.ui = AddWhen.Ui_Dialog()
        self.value = None
        self._block = None
        self.ui.setupUi(self)
        self.__updateBlockType(0)
        self.__updateImage(0)
        self._language = Language()



        for name, pathimg in zip(listNameBlocks,listBlock):
            self.ui.comboBoxBlockImage.addItem(name, userData=(pathimg, nameBlocToConfigBlock(name)))
        self.ui.comboBoxBlockImage.currentIndexChanged.connect(lambda: self.__updateImage(self.ui.comboBoxBlockImage.currentIndex()))
        self.ui.lineEditName.textChanged.connect(lambda: self.__updateImage(self.ui.comboBoxBlockImage.currentIndex()))
        self.ui.Run_start.stateChanged.connect(self.__changeRunStart)

    @Slot()
    def __changeRunStart(self):
        if self.ui.Run_start.isChecked():
            self.ui.lineEditName.setEnabled(False)
            if self.ui.comboBoxBlockImage.currentText() != "block8":
                if self.ui.comboBoxBlockImage.currentIndex() == 0:
                    self.ui.comboBoxBlockImage.setCurrentIndex(1)
                else:
                    self.ui.comboBoxBlockImage.setCurrentIndex(0)
            self.ui.comboBoxBlockImage.setEnabled(False)
            self.ui.lineEditName.setText("start")
            self.__updateImage(self.ui.comboBoxBlockImage.currentIndex())
        else:
            self.ui.lineEditName.setText("")
            self.ui.lineEditName.setEnabled(True)
            self.ui.comboBoxBlockImage.setEnabled(True)
            self.__updateImage(self.ui.comboBoxBlockImage.currentIndex())

    @Slot()
    def __updateImage(self, index):
        self.value = self.translations[Language().language]
        self.nameControl = self.ui.lineEditName.text().replace(" ","_")
        self.img = listNameBlocks[index]
        self.imgName = listBlock[index]
        img = PILImagetoCV2Image(Image.open(self.imgName))
        # if self.block is None:
        self._block = Block(img, self.value, self.nameControl, [], BlockType.WHEN, BlockImgType.COMPLEXBLOCK)
        self._block.renderImg()
        # else:
        #     self.block.img = img
        #     self.block.text1 = self.value
        #     self.block.text2 = self.nameControl
        self.ui.BlockImage.setPixmap(self.block.img.toqpixmap())

    def __updateBlockType(self, index):
        self.blockType = listTypeBlock[index]
        self.config = listconfig[index]

    def __clear(self):
        self.ui.lineEditName.clear()
        self.ui.comboBoxBlockImage.setCurrentIndex(0)

    @property
    def translations(self):
        return self._translations

    def getConfig(self):
        _, self.configImg = self.ui.comboBoxBlockImage.currentData()
        return self.configImg

    @property
    def block(self):
        return self._block
