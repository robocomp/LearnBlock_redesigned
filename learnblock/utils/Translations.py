from PySide2.QtCore import Signal, QObject

from learnblock.utils.Language import Language
from learnblock.utils.Translator import TextTranslator


class ListTranslations(QObject):

    updated = Signal()
    def __init__(self):
        super(ListTranslations, self).__init__()
        self._list = []
        self._language = Language()
        self._translator = TextTranslator()
        self._language.changed.connect(self.changeLanguage)
        # super(ListTranslations, self).__init__(seq)
    def append(self, item):
        self._list.append(item)

    def changeLanguage(self):
        if self._language.language != "EN":
            text=[]
            dicts=[]
            needTranslater = False
            for translation in self._list:
                if self._language.language not in translation:
                    text.append(translation.get("EN").replace("_"," "))
                    dicts.append(translation)
                    needTranslater=True
            if needTranslater:
                try:
                    translations = self._translator.translate(text=text, src="en", dest=self._language.language)
                    for t,translation in zip(translations, dicts):
                        translation.setdefault(self._language.language, t.text.replace(" ", "_"))
                except Exception as e:
                    for t, translation in zip(text, dicts):
                        translation.setdefault(self._language.language, t.replace(" ", "_"))
            self.updated.emit()


class AllTranslations(object):
    instance = None

    def __new__(cls):
        if not TextTranslator.instance:
            TextTranslator.instance = ListTranslations()
        return TextTranslator.instance

    def __getattr__(self, name):
        return getattr(self.instance, name)


class Translations:

    def __init__(self, seq={}, **kwargs):
        self._translations = seq
        self._language = Language()
        AllTranslations().append(self._translations)

    def __getitem__(self, item):
        try:
            return self._translations[item.upper()]
        except Exception as e:
            return self._translations["EN"]

    def keys(self):
        return self._translations.keys()

    @property
    def text(self):
        return self[self._language.language]


if __name__ == '__main__':
    t = Translations({"ES": "principal", "EN": "main"})
    print(t.text)
    Language().language = "ja"
    print(t.text)

    for x in range(1000):
        pass
