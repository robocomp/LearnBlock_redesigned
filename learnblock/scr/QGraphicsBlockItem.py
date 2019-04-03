import json

from PIL import Image
from PySide2.QtGui import QMouseEvent
from PySide2.QtCore import QObject, Qt, QPointF, QTimer
from PySide2.QtGui import QPixmap
from PySide2.QtGui import QImage
from PySide2.QtWidgets import QGraphicsPixmapItem, QGraphicsItem, QMenu, QAction, QGraphicsSceneMouseEvent, \
    QGraphicsSceneHoverEvent

from learnblock.scr.UndoCommands import DeleteCommand
from learnblock.utils import PILImagetoCV2Image
from learnblock.utils.Block import Block
from learnblock.utils.Connection import Connection
from learnblock.utils.Language import Language
from learnblock.utils.Types import BlockType, BlockImgType, ConnectionType, VariableType
from learnblock.utils.point import Point


class KeyPressEater(QObject):
    def eventFilter(self, obj, event):
        if isinstance(event, QMouseEvent) and event.buttons() & Qt.RightButton:
            return True
        return False


class QGraphicsBlockItem(QGraphicsPixmapItem, Block, QObject):

    def __init__(self, _parent, _imgfile: str, _functionname: str, _translations: dict, _vars: list, _connections: dict,
                 _type: BlockType, _typeIMG: BlockImgType, _nameControl: str = ""):
        self._parent = _parent
        self._translations = _translations
        self._vars = _vars
        self.initConections(_connections)
        self._language = Language()
        self.__functionname = _functionname
        self._type = _type
        self._typeImg = _typeIMG
        self._nameControl = _nameControl
        self.c, self.cS = None, None
        # self.timer = QTimer()
        # self.timer.timeout.connect(self.updateSize)
        # self.timer.start(100)
        QObject.__init__(self)

        QGraphicsPixmapItem.__init__(self)
        img = PILImagetoCV2Image(Image.open(_imgfile))

        _varstext = self.listValuesVars()

        Block.__init__(self, _img=img, _text1="", _text2=self._nameControl, _vars=_varstext, _type=self._type, _typeIMG=self._typeImg)

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)
        self.setZValue(1)
        self.initPopUpMenu()
        self._language.changed.connect(self.changeLanguage)
        self.imgchanged.connect(self.repaintImg)
        self.changeLanguage()
        super(QGraphicsBlockItem, self).setPos(QPointF(0, 0))
        # self.setEnabled(False)

    def __str__(self):
        return str(self.id)

    @property
    def functionname(self):
        return self.__functionname

    def initConections(self, conf):
        self._connections = {}
        self._typeImg = BlockImgType.fromString(conf["type"])
        for p in conf["points"]:
            _type = ConnectionType.fromString(p["type"])
            self._connections[_type] = Connection(point=Point(p["x"], p["y"]), parent=self, type=_type)

    def initPopUpMenu(self):
        self.popMenu = QMenu()
        self.keyPressEater = KeyPressEater(self.popMenu)
        self.popMenu.installEventFilter(self.keyPressEater)
        action1 = QAction(self.tr('Edit'), self)
        # action1.triggered.connect(self.on_clicked_menu_edit)
        self.popMenu.addAction(action1)
        if self.__functionname not in ["main", "when"]:
            if self._type is BlockType.USERFUNCTION and self._typeIMG is BlockImgType.COMPLEXBLOCK:
                action3 = QAction(self.tr('Export Block'), self)
                action3.triggered.connect(self.on_clicked_menu_export_block)
                self.popMenu.addAction(action3)
            else:
                action0 = QAction(self.tr('Duplicate'), self)
                action0.triggered.connect(self.on_clicked_menu_duplicate)
                self.popMenu.addAction(action0)

        self.popMenu.addSeparator()
        action2 = QAction(self.tr('Delete'), self)
        action2.triggered.connect(self.on_clicked_menu_delete)
        action2.installEventFilter(self.keyPressEater)
        self.popMenu.addAction(action2)
        # self.pos

    def on_clicked_menu_edit(self):
        raise NotImplementedError("on_clicked_menu_export_block")

    def on_clicked_menu_export_block(self):
        raise NotImplementedError("on_clicked_menu_export_block")

    def on_clicked_menu_duplicate(self):
        raise NotImplementedError("on_clicked_menu_export_block")

    def on_clicked_menu_delete(self):
        if self.scene() is not None:
            self.scene().undoStack.push(DeleteCommand(self, self.scene()))
            # self.scene().removeItem(self)

    def changeLanguage(self):
        self.text1 = self._translations[self._language.language]

    def repaintImg(self):
        self.setPixmap(self.img.toqpixmap())
        for type, c in iter(self._connections.items()):
            otherConnect, otherId = c.connect
            if type is ConnectionType.BOTTOM:
                c.point.move(0, self.pixmap().height() - 5 - c.point.y)
                if otherId is not None:
                    otherConnect.parent.setPos(self.pos() + QPointF(0, self.pixmap().height() - 5), True)
            if type is ConnectionType.RIGHT:
                c.point.move(self.pixmap().width() - 5 - c.point.x, 0)
                if otherId is not None:
                    otherConnect.parent.setPos(self.pos() + QPointF(self.pixmap().width() - 5, 0), True)

    def updateSize(self):
        _, self.block_size = self.getNumSub()
        self._resized()

    def _resized(self):
        if ConnectionType.TOP in self._connections and self._connections[ConnectionType.TOP].connected():
            self._connections[ConnectionType.TOP].connect[0].parent.updateSize()

    def listValuesVars(self):
        return [str(v.value) for v in self._vars]

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent):
        selectedItems = self.scene().selectedItems()
        if self in selectedItems:
            for item in selectedItems:
                item.setHover(True)
        else:
            self.setHover(True)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent):
        selectedItems = self.scene().selectedItems()
        if self in selectedItems:
            for item in selectedItems:
                item.setHover(False)
        else:
            self.setHover(False)

    def setHover(self, hover):
        self.hover = hover
        if ConnectionType.BOTTOM in self._connections and self._connections[ConnectionType.BOTTOM].connected():
            self._connections[ConnectionType.BOTTOM].connect[0].parent.setHover(hover)
        if ConnectionType.RIGHT in self._connections and self._connections[ConnectionType.RIGHT].connected():
            self._connections[ConnectionType.RIGHT].connect[0].parent.setHover(hover)
        if ConnectionType.BOTTOMIN in self._connections and self._connections[ConnectionType.BOTTOMIN].connected():
            self._connections[ConnectionType.BOTTOMIN].connect[0].parent.setHover(hover)

    def setZValue(self, z: float):
        super(QGraphicsBlockItem, self).setZValue(z)
        if ConnectionType.BOTTOM in self._connections and self._connections[ConnectionType.BOTTOM].connected():
            self._connections[ConnectionType.BOTTOM].connect[0].parent.setZValue(z)
        if ConnectionType.RIGHT in self._connections and self._connections[ConnectionType.RIGHT].connected():
            self._connections[ConnectionType.RIGHT].connect[0].parent.setZValue(z)
        if ConnectionType.BOTTOMIN in self._connections and self._connections[ConnectionType.BOTTOMIN].connected():
            self._connections[ConnectionType.BOTTOMIN].connect[0].parent.setZValue(z)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        if self.isEnabled():
            self.setZValue(1)
            if event.button() is Qt.MouseButton.LeftButton:
                pass
                # self.posmouseinItem = event.scenePos() - self.pos()
                # items = self.scene().selectedItems()
                # if self not in items:
                #     self.scene().clearSelection()
                # if self.DialogVar is not None:
                #     self.DialogVar.close()
            if event.button() is Qt.MouseButton.RightButton:
                self.popMenu.exec_(event.screenPos())

    def setPos(self, pos: QPointF, connect=False):
        super(QGraphicsBlockItem, self).setPos(pos)
        for type, c in iter(self._connections.items()):
            otherConnect, otherId = c.connect
            if otherId is not None:
                if type in [ConnectionType.TOP, ConnectionType.LEFT] and not connect:
                    c.connect = None
                    otherConnect.connect = None
                    otherConnect.parent.updateSize()
                elif c.type is ConnectionType.BOTTOM:
                    otherConnect.parent.setPos(self.pos() + QPointF(0, self.pixmap().height() - 5), True)
                elif c.type is ConnectionType.BOTTOMIN:
                    otherConnect.parent.setPos(self.pos() + QPointF(17, 33), True)
                elif c.type is ConnectionType.RIGHT:
                    otherConnect.parent.setPos(self.pos() + QPointF(self.pixmap().width() - 5, 0), True)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        self.setZValue(-1)
        self.scene().imgPosibleConnectH.setVisible(False)
        self.scene().imgPosibleConnectV.setVisible(False)
        self.connecting()

    def getLastItem(self):
        if ConnectionType.BOTTOM in self._connections:
            c = self._connections[ConnectionType.BOTTOM]
            if c.connect[0] is None:
                return c
            else:
                return c.connect[0].parent.getLastItem()
        return None

    def getLastRightItem(self):
        if ConnectionType.RIGHT in self._connections:
            c = self._connections[ConnectionType.RIGHT]
            if c.connect[0] is None:
                return c
            else:
                return c.connect[0].parent.getLastRightItem()
        return None

    def connecting(self):
        if self.c is None or self.cS is None:
            return
        if self.cS.connect[0] is self.c:
            return
        if self.c.connect[0] is not None:
            if self.c.type is ConnectionType.TOP:
                pass
            elif self.c.type in [ConnectionType.BOTTOM, ConnectionType.BOTTOMIN]:
                cNext, _ = self.c.connect
                cLastIt = self.getLastItem()
                if cLastIt is not None:
                    cLastIt.connect = cNext
                    cNext.connect = cLastIt
            elif self.c.type is ConnectionType.RIGHT:
                cNext, _ = self.c.connect
                cLastIt = self.getLastRightItem()
                if cLastIt is not None:
                    cLastIt.connect = cNext
                    cNext.connect = cLastIt
        self.c.connect = self.cS
        self.cS.connect = self.c
        otherBlock = self.c.parent
        if self.c.type is ConnectionType.TOP:
            self.setPos(otherBlock.pos() + QPointF(0, - otherBlock.pixmap().height() + 5), True)
        elif self.c.type is ConnectionType.BOTTOM:
            self.setPos(otherBlock.pos() + QPointF(0, otherBlock.pixmap().height() - 5), True)
        elif self.c.type is ConnectionType.RIGHT:
            self.setPos(otherBlock.pos() + QPointF(otherBlock.pixmap().width() - 5, 0), True)
        elif self.c.type is ConnectionType.LEFT:
            self.setPos(otherBlock.pos() + QPointF(-otherBlock.pixmap().width() + 5, 0), True)
        elif self.c.type is ConnectionType.BOTTOMIN:
            self.setPos(otherBlock.pos() + QPointF(17, 33), True)
        self.updateSize()

    def getNumSubBottom(self, n=0, size=0):
        size += self.pixmap().height() - 5
        if ConnectionType.BOTTOM in self._connections:
            c = self._connections[ConnectionType.BOTTOM]
            if c.connect[1] is None:
                return n + 1, size + 1
            else:
                return c.connect[0].parent.getNumSubBottom(n + 1, size)
        return n + 1, size + 1

    def getNumSub(self, n=0):
        if ConnectionType.BOTTOMIN in self._connections:
            c = self._connections[ConnectionType.BOTTOMIN]
            if c.connect[1] is None:
                return 0, 34
            else:
                return c.connect[0].parent.getNumSubBottom()
        return 0, 34

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        super(QGraphicsBlockItem, self).mouseMoveEvent(event)
        self.setPos(event.scenePos() - event.buttonDownPos(Qt.MouseButton.LeftButton))
        self.c, self.cS = self.closestItem()
        imgPosibleConnectH = self.scene().imgPosibleConnectH
        imgPosibleConnectV = self.scene().imgPosibleConnectV
        if self.c is not None:
            if self.c.type is ConnectionType.TOP:
                imgPosibleConnectH.setPos(self.c.parent.pos())
                imgPosibleConnectH.setVisible(True)
                imgPosibleConnectH.setZValue(1)
            elif self.c.type is ConnectionType.BOTTOM:
                imgPosibleConnectH.setPos(self.c.parent.pos() + QPointF(0, self.c.parent.pixmap().height() - 5))
                imgPosibleConnectH.setVisible(True)
                imgPosibleConnectH.setZValue(1)
            elif self.c.type is ConnectionType.RIGHT:
                imgPosibleConnectV.setPos(
                    self.c.parent.pos() + QPointF(self.c.parent.pixmap().width() - 5, 0) + QPointF(0, 5))
                imgPosibleConnectV.setVisible(True)
                imgPosibleConnectV.setZValue(1)
            elif self.c.type is ConnectionType.LEFT:
                imgPosibleConnectV.setPos(self.c.parent.pos() + QPointF(0, 5))
                imgPosibleConnectV.setVisible(True)
                imgPosibleConnectV.setZValue(1)
            elif self.c.type is ConnectionType.BOTTOMIN:
                imgPosibleConnectH.setPos(self.c.parent.pos() + QPointF(16, 38))
                imgPosibleConnectH.setVisible(True)
                imgPosibleConnectH.setZValue(1)
        else:
            imgPosibleConnectH.setVisible(False)
            imgPosibleConnectV.setVisible(False)

    def closestItem(self):
        min_dist = None
        min_c = None
        min_cS = None
        if self.scene() is not None:
            sceneitems = self.scene().items()
        else:
            sceneitems = []
        sceneitems = [x for x in sceneitems if isinstance(x, QGraphicsBlockItem)]
        for type, c in iter(self._connections.items()):
            for otherItem in sceneitems:
                if self is not otherItem and otherItem.isEnabled():
                    for othertype, otherc in iter(otherItem._connections.items()):
                        if (type is ConnectionType.TOP and othertype in [ConnectionType.BOTTOMIN,
                                                                         ConnectionType.BOTTOM]) or \
                                (type is ConnectionType.LEFT and othertype is ConnectionType.RIGHT):
                            dist = c.pos.distance(otherc.pos)
                            if min_dist is None or dist < min_dist:
                                min_c = otherc
                                min_cS = c
                                min_dist = dist
        self.setZValue(1)
        if min_dist is not None and min_dist < 30:
            return min_c, min_cS
        return None, None

    def getInstructionsByType(self, type: ConnectionType):
        if type in self._connections and self._connections[type].connected():
            inst = self._connections[type].connect[0].parent.getInstructions()
            return inst
        return None

    def getInstructions(self):
        instRight = self.getInstructionsByType(ConnectionType.RIGHT)
        instBottom = self.getInstructionsByType(ConnectionType.BOTTOM)
        instBottomIn = self.getInstructionsByType(ConnectionType.BOTTOMIN)
        nameControl = self._nameControl
        if nameControl is "":
            nameControl = None
        dic = dict(NAMECONTROL=nameControl, RIGHT=instRight, BOTTOM=instBottom, BOTTOMIN=instBottomIn, VARIABLES=self.getVars(), TYPE=self._type)
        return self.__functionname, dic

    def getVars(self):
        vars = []
        for var in self._vars:
            value = str(var.value)
            if var.type in [VariableType.APRILTEXT, VariableType.STRING]:
                value = '"' + value + '"'
            vars.append(value)
        if len(vars) is 0:
            vars = None
        return vars

    def isBlockDef(self):
        return (self.__functionname == "when") or (
                    len(self._connections) is 1 and ConnectionType.BOTTOMIN in self._connections)

    def setEnabled(self, enabled:bool):
        super(QGraphicsBlockItem, self).setEnabled(enabled)
        if not enabled:
            _, _, _, a = self.img.split()
            img = self.img.convert('L').convert('RGB')
            img.putalpha(a)
        else:
            img = self.img
        self.setPixmap(img.toqpixmap())
        for _type in [ConnectionType.BOTTOMIN, ConnectionType.BOTTOM, ConnectionType.RIGHT]:
            if _type in self._connections and self._connections[_type].connected():
                self._connections[_type].connect[0].parent.setEnabled(enabled)
