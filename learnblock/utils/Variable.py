from PySide2.QtCore import Signal

from learnblock.utils.Types import VariableType


class Variable(object):

    changed = Signal()
    def __init__(self, _type, name, default, translate):
        self._type = _type
        self._name = name
        self._value = default
        self._translate = translate

    @property
    def value(self):
        return VariableType.getValue(self._type, self._value)

    @value.setter
    def value(self, _value):
        self._value = _value
        self.changed.emint()

    def getName(self, keylanguage):
        return self._translate.get(keylanguage.upper())

    def __str__(self):
        return "type      = " + self._type + "\n" \
               "name      = " + self._name + "\n"\
               "default   = " + self._value + "\n" \
               "translate = " + str(self._translate) + "\n"
