import os

from PIL import ImageFont

from learnblock import PATHFONT, Language


class _Font:

    def __init__(self):
        self.__font = ImageFont.truetype(os.path.join(PATHFONT, "ESEN.ttf"), 20)
        self.fonts = os.listdir(PATHFONT)

        self.language = Language()
        self.language.changed.connect(self.reloadFont)

    def reloadFont(self):
        for f in self.fonts:
            if self.language.language in f:
                self.__font = ImageFont.truetype(os.path.join(PATHFONT, f), 20)
                break

    @property
    def font(self):
        return self.__font


class Font:

    instance = None

    def __new__(cls):
        if not Font.instance:
            Font.instance = _Font()
        return Font.instance

    def __getattr__(self, name):
        return getattr(self.instance, name)
