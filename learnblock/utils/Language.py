from PySide2.QtCore import QObject, Signal
from singleton_decorator import singleton


@singleton
class Language(QObject):
    changed = Signal(str)

    def __init__(self):
        QObject.__init__(self)
        self.__language = "EN"

    @property
    def language(self):
        return self.__language

    @language.setter
    def language(self, _language):
        self.__language = _language.upper()
        self.changed.emit(str(self.__language))

