from PySide2.QtCore import QPointF
from PySide2.QtWidgets import QUndoCommand, QGraphicsScene

from learnblock.scr import QGraphicsBlockItem


class MoveCommand(QUndoCommand):

    def __init__(self, item: QGraphicsBlockItem, oldPos: QPointF, scene: QGraphicsScene):
        self._item = item
        self._newPos = item.pos()
        self._oldPos = oldPos
        self._scene = scene
        super(MoveCommand, self).__init__()

    def undo(self):
        self._item.setPos(self._oldPos)
        self._item.c, self._item.cS = self._item.closestItem()
        self._item.connecting()
        self._scene.update()

    def redo(self):
        self._item.setPos(self._newPos)
        self._item.c, self._item.cS = self._item.closestItem()
        self._item.connecting()
        self._scene.update()

    def mergeWith(self, other: QUndoCommand):
        if self is other:
            return False
        self._newPos = other._item.pos()
        return True


class AddCommand(QUndoCommand):

    def __init__(self, item: QGraphicsBlockItem, scene: QGraphicsScene, parent: QUndoCommand = None):
        self._item = item
        self._scene = scene
        self._initialposition = item.pos()
        self._scene.update()
        super(AddCommand, self).__init__(parent)

    def undo(self):
        self._scene.removeItem(self._item)
        self._scene.update()
        if self._item.functionname == "main":
            self._item._parent.setEnabled(True)

    def redo(self):
        self._scene.addItem(self._item, True)
        self._item.setPos(self._initialposition)
        self._scene.clearSelection()
        self._scene.update()
        if self._item.functionname == "main":
            self._item._parent.setEnabled(False)


class DeleteCommand(QUndoCommand):

    def __init__(self, item: QGraphicsBlockItem, scene: QGraphicsScene, parent: QUndoCommand = None):
        self._item = item
        self._scene = scene
        super(DeleteCommand, self).__init__(parent)

    def undo(self):
        self._scene.addItem(self._item, True)
        self._item.c, self._item.cS = self._item.closestItem()
        self._item.connecting()
        self._scene.update()
        if self._item.functionname == "main":
            self._item._parent.setEnabled(False)

    def redo(self):
        self._scene.removeItem(self._item)
        if self._item.functionname == "main":
            self._item._parent.setEnabled(True)

