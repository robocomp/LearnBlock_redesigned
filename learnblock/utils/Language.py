from PySide2.QtCore import QObject, Signal


class SigLanguage(QObject):
    changed = Signal(str)

    def __init__(self):
        QObject.__init__(self)
        # super(SigLanguage, self).__init__()
        self.__language = "EN"

    @property
    def language(self):
        return self.__language

    @language.setter
    def language(self, _language):
        self.__language = _language.upper()
        self.changed.emit(str(self.__language))


class Language():

    instance = None

    def __new__(cls):
        if not Language.instance:
            Language.instance = SigLanguage()
        return Language.instance

    def __getattr__(self, name):
        return getattr(self.instance, name)

# class Language(QObject):
#     changed = Signal(str)
#
#     def __init__(self):
#         super(Language, self).__init__()
#         self.__language = None
#
#     @property
#     def language(self):
#         return self.__language
#
#     @language.setter
#     def language(self, _language):
#         self.__language = _language.upper()
#         self.changed.emit(str(self.__language))
