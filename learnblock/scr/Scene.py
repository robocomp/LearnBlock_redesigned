import os

from PySide2.QtCore import Qt
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QGraphicsScene, QGraphicsItem, QGraphicsPixmapItem, QUndoStack, QGraphicsSceneMouseEvent, \
    QMenu

from learnblock import PATHBLOCKSIMG
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
        undoAction = self.undoStack.createUndoAction(self, self.tr("&Undo"))
        undoAction.setShortcuts(QKeySequence.Undo)
        self.popMenu.addAction(undoAction)

        redoAction = self.undoStack.createRedoAction(self, self.tr("&Redo"))
        redoAction.setShortcuts(QKeySequence.Redo)
        self.popMenu.addAction(redoAction)

    def addItem(self, item: QGraphicsItem, fromStack=False):
        if fromStack:
            super(Scene, self).addItem(item)
        else:
            self.undoStack.push(AddCommand(item, self))

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        if event.button() is Qt.MouseButton.RightButton:
            self.popMenu.exec_(event.screenPos())
        movingItem = self.itemAt(event.scenePos(), self.view.transform())
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
