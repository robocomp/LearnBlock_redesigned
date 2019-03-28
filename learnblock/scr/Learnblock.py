import os
import sys

from PySide2.QtCore import QTranslator, QLibraryInfo
from PySide2.QtWidgets import QMainWindow, QApplication

from learnblock import PATHLANGUAGES
from learnblock.guis import Learnblock
from learnblock.scr.ButtonBlock import ButtonBlock
from learnblock.scr.Scene import Scene
from learnblock.scr.View import View
from learnblock.utils.Functions import load_blocks_Config
from learnblock.utils.Language import Language
from learnblock.utils.Types import BlockType


class LearnBlock(QMainWindow):

    def __init__(self):
        self.app = QApplication(sys.argv)
        QMainWindow.__init__(self)
        self.ui = Learnblock.Ui_MainWindow()
        self.ui.setupUi(self)
        self.language = Language()

        # Load Translators
        self.initTranslators()
        self.changeLanguage()

        self._view = View(None, self.ui.frame)
        self._view.setObjectName("view")
        self.ui.verticalLayout_3.addWidget(self._view)
        self._scene = Scene(self, self._view)
        self._view.setScene(self._scene)
        self._view.show()
        self._view.setZoom(False)

        self._view.setScene(self._scene)
        self._view.show()
        self._view.setZoom(False)

        # Connect UI
        self.ui.language.currentIndexChanged.connect(self.changeLanguage)
        self.ui.splitter.splitterMoved.connect(self.resizeFunctionTab)

        self.showMaximized()
        self.initBlocks()
        self.language.changed.emit("en")

        r = self.app.exec_()
        sys.exit(r)

    @property
    def scene(self):
        return self._scene

    def resizeFunctionTab(self):
        self.pre_sizes = self.ui.splitter.sizes()
        width = self.ui.functions.width() - 51
        tables = list(self.dicTables.values()) + [self.ui.tableSearch]
        for v in tables:
            v.setColumnWidth(0, width - 20)
            # for item in [v.cellWidget(r, 0) for r in range(v.rowCount())]:
            #     item.updateIconSize(width - 20)

    def initTranslators(self):
        combobox = self.ui.language
        combobox.clear()
        for file in os.listdir(PATHLANGUAGES):
            if os.path.splitext(file)[1] == ".qm":
                translator = QTranslator()
                print('Localization loaded: ', os.path.join(PATHLANGUAGES, file),
                      translator.load(file, PATHLANGUAGES))
                qttranslator = QTranslator()
                print('Localization loaded: ',
                      os.path.join(QLibraryInfo.location(QLibraryInfo.TranslationsPath), "q" + file),
                      qttranslator.load("q" + file, QLibraryInfo.location(QLibraryInfo.TranslationsPath)))
                combobox.addItem(file[2:-3], (translator, qttranslator, file[2:-3]))

    def initBlocks(self):
        self.dicTables = {BlockType.CONTROL: self.ui.tableControl, BlockType.MOTOR: self.ui.tableMotor,
                          BlockType.PERCEPTUAL: self.ui.tablePerceptual,
                          BlockType.PROPIOPERCEPTIVE: self.ui.tablePropioperceptive, BlockType.OPERATOR: self.ui.tableOperadores,
                          BlockType.VARIABLE: self.ui.tableVariables,
                          BlockType.USERFUNCTION: self.ui.tableUserfunctions, BlockType.EXPRESS: self.ui.tableExpress,
                          BlockType.OTHERS: self.ui.tableOthers}

        for table in iter(self.dicTables.values()):
            table.verticalHeader().setVisible(False)
            table.horizontalHeader().setVisible(False)
            table.setColumnCount(1)
            table.setRowCount(0)
        config = load_blocks_Config()
        for b in config:
            _type = BlockType.fromString(b["type"])
            table = self.dicTables[_type]
            b.setdefault("variables", [])
            b.setdefault("languages", {})
            b.setdefault("tooltip", {})
            for _img in b["img"]:
                table.insertRow(table.rowCount())
                button = ButtonBlock(self, _table=table, _row=table.rowCount()-1, _imgfileconf=_img, _functionmame=b["name"],
                            _language=self.language, _translations=b["languages"], _tooltips=b["tooltip"],
                            _vars=b["variables"],_type=_type)
                table.setCellWidget(table.rowCount() - 1, 0, button)

    def changeLanguage(self):
        translator, qttranslator, language = self.ui.language.currentData()
        self.app.installTranslator(translator)
        self.app.installTranslator(qttranslator)
        self.ui.retranslateUi(self)
        self.language.language = language



if __name__ == '__main__':
    LearnBlock()