import json
import os
import sys
import traceback

from PySide2.QtCore import QTranslator, QLibraryInfo, Slot
from PySide2.QtWidgets import QMainWindow, QApplication, QMessageBox
from googletrans import LANGUAGES

from learnblock import PATHLANGUAGES
from learnblock.guis import Learnblock
from learnblock.scr.ButtonBlock import ButtonBlock
from learnblock.scr.Scene import Scene
from learnblock.scr.View import View
from learnblock.utils.Functions import load_blocks_Config
from learnblock.utils.Language import Language
from learnblock.utils.ParserBlocks import ParserBlocks
from learnblock.utils.ParserTBlockCode import parserfromTBlockCode, ParseException
from learnblock.utils.Translator import TextTranslator
from learnblock.utils.Types import BlockType
from learnblock.utils.Translations import AllTranslations


class LearnBlock(QMainWindow):

    def __init__(self):
        self.app = QApplication(sys.argv)
        QMainWindow.__init__(self)
        self.ui = Learnblock.Ui_MainWindow()
        self.configs = {}
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

        # Parser
        self._parserblocks = ParserBlocks()

        # Connect UI
        self.ui.language.currentIndexChanged.connect(self.changeLanguage)
        self.ui.splitter.splitterMoved.connect(self.resizeFunctionTab)
        self.translations = AllTranslations()
        self.translations.updated.connect(self.saveConfig)
        self.ui.block2textpushButton.clicked.connect(self.blocksToText)

        self.showMaximized()
        self.initBlocks()
        self.language.changed.emit("en")

        r = self.app.exec_()
        sys.exit(r)

    @Slot()
    def saveConfig(self):
        for file, v in self.configs.items():
            with open(file, 'w') as fp:
                json.dump(v, fp, sort_keys=True, indent=4)

    @property
    def scene(self):
        return self._scene

    @Slot()
    def resizeFunctionTab(self):
        self.pre_sizes = self.ui.splitter.sizes()
        width = self.ui.functions.width() - 51
        tables = list(self.dicTables.values()) + [self.ui.tableSearch]
        for v in tables:
            v.setColumnWidth(0, width - 20)

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
        for l in sorted(LANGUAGES):
            combobox.addItem(l, (translator, qttranslator, l))

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
        self.configs = load_blocks_Config()
        for blocks in self.configs.values():
            for b in blocks:
                _type = BlockType.fromString(b["type"])
                table = self.dicTables[_type]
                for _img in b["img"]:
                    table.insertRow(table.rowCount())
                    b.setdefault("variables", [])
                    b.setdefault("languages", {"EN": b["name"]})
                    b.setdefault("tooltip", b["languages"])
                    button = ButtonBlock(self, _table=table, _row=table.rowCount()-1, _imgfileconf=_img, _functionmame=b["name"],
                                _translations=b["languages"], _tooltips=b["tooltip"],
                                _vars=b["variables"],_type=_type)
                    table.setCellWidget(table.rowCount() - 1, 0, button)

    @Slot()
    def changeLanguage(self):
        translator, qttranslator, language = self.ui.language.currentData()
        self.app.installTranslator(translator)
        self.app.installTranslator(qttranslator)
        self.ui.retranslateUi(self)
        self.language.language = language

    def blocksToText(self):
        name_Client = self.ui.clientscomboBox.currentText()
        self.blocksToTextCode()
        self.TBlocCodeToPython(name_Client)

    def TBlocCodeToPython(self, name_Client):
        textCode = self.ui.textCode.toPlainText()
        try:
            code = parserfromTBlockCode(textCode, name_Client)
            if not code:
                msgBox = QMessageBox()
                msgBox.setWindowTitle(self.tr("Warning"))
                msgBox.setIcon(QMessageBox.Warning)
                msgBox.setText(self.tr("Your code is empty or is not correct"))
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.setDefaultButton(QMessageBox.Ok)
                msgBox.exec_()
            self.ui.pythonCode.clear()
            self.ui.pythonCode.setText(code)
            return code
        except ParseException as e:
            traceback.print_exc()
            msgBox = QMessageBox()
            msgBox.setWindowTitle(self.tr("Warning"))
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setText(self.tr("line: {}".format(e.line) + "\n    " + " " * e.col + "^"))
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.setDefaultButton(QMessageBox.Ok)
            msgBox.exec_()
        except Exception as e:
            msgBox = QMessageBox()
            msgBox.setWindowTitle(self.tr("Warning"))
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setText(e)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.setDefaultButton(QMessageBox.Ok)
            msgBox.exec_()
        return False

    def blocksToTextCode(self):
        text = ""
        # for library in self.listLibrary:              # TODO add variables
        #     text = 'import "' + library[0] + '"\n'
        # if len(self.listNameVars) > 0:
        #     for name in self.listNameVars:
        #         text += name + " = None\n"
        blocks = self.scene.getListInstructions()
        code = self._parserblocks.parserBlocks(blocks)
        self.ui.textCode.clear()
        self.ui.textCode.setText(text + code)



if __name__ == '__main__':
    LearnBlock()