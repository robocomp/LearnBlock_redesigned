from PySide2.QtCore import Slot
from PySide2.QtWidgets import QGraphicsView, QGraphicsScene

from learnblock.scr.Scene import MoveCommand


class View(QGraphicsView):

    def __init__(self, scene: QGraphicsScene, parent, arg=None):
        self.zoom = None
        super(View, self).__init__(scene, parent)
        # QGraphicsView.__init__(self, scene, parent)

    def setZoom(self, zoom):
        self.zoom = zoom

    def wheelEvent(self, event):
        if self.zoom:
            # Zoom Factor
            zoomInFactor = 1.25
            zoomOutFactor = 1 / zoomInFactor

            # Set Anchors
            self.setTransformationAnchor(QGraphicsView.NoAnchor)
            self.setResizeAnchor(QGraphicsView.NoAnchor)

            # Save the scene pos
            oldPos = self.mapToScene(event.pos())

            # Zoom
            if event.delta() > 0:
                zoomFactor = zoomInFactor
            else:
                zoomFactor = zoomOutFactor
            self.scale(zoomFactor, zoomFactor)

            # Get the new position
            newPos = self.mapToScene(event.pos())

            # Move scene to old position
            delta = newPos - oldPos
            self.translate(delta.x(), delta.y())
