import os

from PySide2.QtCore import Qt
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QGraphicsScene, QGraphicsItem, QGraphicsPixmapItem, QUndoStack, QGraphicsSceneMouseEvent, \
    QMenu, QAction

from learnblock import PATHBLOCKSIMG
from learnblock.scr.QGraphicsBlockItem import QGraphicsBlockItem
from learnblock.scr.UndoCommands import MoveCommand, AddCommand


class Scene(QGraphicsScene):

    def __init__(self, parent=None, view=None):
        QGraphicsScene.__init__(self, parent)
        self.undoStack = QUndoStack(self)
        # super(Scene, self).__init__(parent)
        self.view = view
        self.imgPosibleConnectH = QGraphicsPixmapItem(os.path.join(PATHBLOCKSIMG, "ConnectH.png"))
        super(Scene, self).addItem(self.imgPosibleConnectH)
        self.imgPosibleConnectH.setVisible(False)
        self.imgPosibleConnectV = QGraphicsPixmapItem(os.path.join(PATHBLOCKSIMG, "ConnectV.png"))
        super(Scene, self).addItem(self.imgPosibleConnectV)
        self.imgPosibleConnectV.setVisible(False)
        self.oldPos = None
        self.createActions()

    def createActions(self):
        self.popMenu = QMenu()
        self.undoAction = self.undoStack.createUndoAction(self, self.tr("&Undo"))
        self.undoAction.setShortcuts(QKeySequence.Undo)
        self.popMenu.addAction(self.undoAction)

        self.redoAction = self.undoStack.createRedoAction(self, self.tr("&Redo"))
        self.redoAction.setShortcuts(QKeySequence.Redo)
        self.popMenu.addAction(self.redoAction)

        self.disableAction = QAction(self.tr("&Disable"), self)
        self.disableAction.triggered.connect(self.setEnabledMain)
        self.popMenu.addAction(self.disableAction)

    def setEnabledMain(self):
        for item in self.items():
            if isinstance(item, QGraphicsBlockItem) and item.isBlockDef():
                if item.functionname == "main":
                    item.setEnabled(not item.isEnabled())
                elif item.functionname == "when":
                    item.setEnabled(not item.isEnabled())

    def addItem(self, item: QGraphicsItem, fromStack=False):
        if fromStack:
            super(Scene, self).addItem(item)
        else:
            self.undoStack.push(AddCommand(item, self))

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):

        movingItem = self.itemAt(event.scenePos(), self.view.transform())
        if movingItem is None and event.button() is Qt.MouseButton.RightButton:
            self.popMenu.exec_(event.screenPos())
        if movingItem is not None and event.button() is Qt.MouseButton.LeftButton:
            self.oldPos = movingItem.pos()
        self.clearSelection()
        super(Scene, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        if len(self.selectedItems()) is not 0:
            movingItem = self.selectedItems()[0]
        else:
            movingItem = None
        if movingItem is not None and event.button() is Qt.MouseButton.LeftButton:
            if self.oldPos is not movingItem.pos():
                self.undoStack.push(MoveCommand(movingItem, self.oldPos, self))
        super(Scene, self).mouseReleaseEvent(event)

    def getListInstructions(self):
        list = []
        for item in self.items():
            if isinstance(item, QGraphicsBlockItem) and item.isBlockDef() and item.isEnabled():
                inst = item.getInstructions()
                list.append(inst)
        return list
