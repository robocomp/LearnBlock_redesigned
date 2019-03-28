from PySide2.QtCore import QObject, Signal


class Language(QObject):
    changed = Signal(str)

    def __init__(self):
        super(Language, self).__init__()
        self.__language = None

    @property
    def language(self):
        return self.__language

    @language.setter
    def language(self, _language):
        self.__language = _language.upper()
        self.changed.emit(str(self.__language))
