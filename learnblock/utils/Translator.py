from googletrans import Translator


class TextTranslator(object):
    instance = None

    def __new__(cls):
        if not TextTranslator.instance:
            TextTranslator.instance = Translator()

        return TextTranslator.instance

    def __getattr__(self, name):
        return getattr(self.instance, name)
