from enum import Enum


class BlockImgType(Enum):
    SIMPLEBLOCK = 1
    COMPLEXBLOCK = 2

    @classmethod
    def fromString(cls, str):
        return getattr(cls, str)


class ConnectionType(Enum):
    TOP = 0
    BOTTOM = 1
    RIGHT = 2
    LEFT = 3
    BOTTOMIN = 4

    @classmethod
    def fromString(cls, str):
        return getattr(cls, str)


class VariableType(Enum):
    FLOAT = float
    STRING = str
    BOOLEAN = bool
    APRILTEXT = str
    INT = int

    @classmethod
    def fromString(cls, str):
        return getattr(cls, str)

    @staticmethod
    def getValue(_type, _value):
        if isinstance(_type, str):
            _type = VariableType.fromString(_type)
        return _type.value(_value)


class BlockType(Enum):
    CONTROL = 0
    MOTOR = 1
    PERCEPTUAL = 2
    PROPIOPERCEPTIVE = 3
    OPERATOR = 4
    EXPRESS = 5
    OTHERS = 6
    FUNCTION = 7
    USERFUNCTION = 8
    LIBRARY = 9
    VARIABLE = 10
    STRING = 11
    NUMBER = 12
    WHEN = 13

    @classmethod
    def fromString(cls, str):
        return getattr(cls, str)

    @staticmethod
    def isfunction(other):
        return other in [BlockType.MOTOR, BlockType.PERCEPTUAL, BlockType.PROPIOPERCEPTIVE, BlockType.EXPRESS,
                         BlockType.FUNCTION, BlockType.OTHERS, BlockType.USERFUNCTION, BlockType.LIBRARY]


class Colors(Enum):
    HUE_CONTROL = 0
    HUE_MOTOR = 0
    HUE_PERCEPTUAL = 60
    HUE_PROPIOPERCEPTIVE = 80
    HUE_OPERATOR = 120
    HUE_EXPRESS = 160
    HUE_OTHERS = 200
    HUE_USERFUNCTION = 240
    HUE_LIBRARY = 240
    HUE_VARIABLE = 20
    HUE_STRING = 75
    HUE_NUMBER = 40
    HUE_WHEN = 50

    @classmethod
    def fromString(cls, str):
        return getattr(cls, str)

    @classmethod
    def fromBlockType(cls, type: BlockType):
        return getattr(cls, "HUE_" + type._name_)


if __name__ == '__main__':
    print(Colors.fromBlockType(BlockType.WHEN).value)
