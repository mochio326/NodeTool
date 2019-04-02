# -*- coding: utf-8 -*-
from .vendor.Qt import QtCore, QtGui, QtWidgets
import uuid


class View(QtWidgets.QGraphicsView):
    """
    QGraphicsView for displaying the nodes.

    :param scene: QGraphicsScene.
    :param parent: QWidget.
    """

    def __init__(self, scene, parent):
        super(View, self).__init__(parent)
        self.setObjectName('View')
        self.setScene(scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.SmartViewportUpdate)
        self.drag = False
        self._clipboard = None
        self.add_items = []
        self._operation_history = [None]
        self._current_operation_history = 0
        self.setStyleSheet('background-color: rgb(40,40,40);')

    def drawBackground(self, painter, rect):
        scene_height = self.sceneRect().height()
        scene_width = self.sceneRect().width()

        # Pen.
        pen = QtGui.QPen()
        pen.setStyle(QtCore.Qt.SolidLine)
        pen.setWidth(1)
        pen.setColor(QtGui.QColor(80, 80, 80, 125))

        sel_pen = QtGui.QPen()
        sel_pen.setStyle(QtCore.Qt.SolidLine)
        sel_pen.setWidth(1)
        sel_pen.setColor(QtGui.QColor(125, 125, 125, 125))

        grid_width = 20
        grid_height = 20
        grid_horizontal_count = int(round(scene_width / grid_width)) + 1
        grid_vertical_count = int(round(scene_height / grid_height)) + 1

        for x in range(0, grid_horizontal_count):
            xc = x * grid_width
            if x % 5 == 0:
                painter.setPen(sel_pen)
            else:
                painter.setPen(pen)
            painter.drawLine(xc, 0, xc, scene_height)

        for y in range(0, grid_vertical_count):
            yc = y * grid_height
            if y % 5 == 0:
                painter.setPen(sel_pen)
            else:
                painter.setPen(pen)
            painter.drawLine(0, yc, scene_width, yc)

    def wheelEvent(self, event):
        """
        Zooms the QGraphicsView in/out.

        :param event: QGraphicsSceneWheelEvent.
        """
        in_factor = 1.25
        out_factor = 1 / in_factor
        old_pos = self.mapToScene(event.pos())
        if event.delta() > 0:
            zoom_factor = in_factor
        else:
            zoom_factor = out_factor
        self.scale(zoom_factor, zoom_factor)
        new_pos = self.mapToScene(event.pos())
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton and event.modifiers() == QtCore.Qt.AltModifier:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self.drag = True
            self.prev_pos = event.pos()
            self.setCursor(QtCore.Qt.SizeAllCursor)
        elif event.button() == QtCore.Qt.LeftButton:
            self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        super(View, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drag:
            # 等倍scaleかつ回転してないはずでscale取り出す…
            new_scale = self.matrix().m11()
            delta = (self.mapToScene(event.pos()) - self.mapToScene(self.prev_pos)) * -1.0 * new_scale
            center = QtCore.QPoint(self.viewport().width() / 2 + delta.x(), self.viewport().height() / 2 + delta.y())
            new_center = self.mapToScene(center)
            self.centerOn(new_center)
            self.prev_pos = event.pos()
            return
        super(View, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.drag:
            self.drag = False
            self.setCursor(QtCore.Qt.ArrowCursor)
        super(View, self).mouseReleaseEvent(event)

    def keyPressEvent(self, event):

        if event.key() == QtCore.Qt.Key_F:
            self.selected_item_focus()
            return

        if event.key() == QtCore.Qt.Key_A:
            self.all_item_focus()
            return

        if event.key() == QtCore.Qt.Key_Delete:
            self._delete()
            return

    def selected_item_focus(self):
        self.focus(self.scene().selectedItems())

    def all_item_focus(self):
        self.focus(self.add_items)

    def focus(self, items):
        if len(items) == 0:
            return
        self.resetMatrix()
        rect = QtCore.QRectF(0, 0, 0, 0)
        for _i in items:
            rect = rect.united(_i.sceneBoundingRect())
        center = QtCore.QPoint(rect.width() / 2 + rect.x(), rect.height() / 2 + rect.y())
        w_s = self.width() / rect.width()
        h_s = self.height() / rect.height()
        zoom_factor = w_s if w_s < h_s else h_s
        zoom_factor = zoom_factor * 0.9
        self.scale(zoom_factor, zoom_factor)
        self.centerOn(center)

    def add_node_on_center(self, node):
        self.add_item(node)
        _pos = self.mapToScene(self.width() / 2, self.height() / 2)
        node.setPos(_pos)
        node.deploying_port()
        node.update()

    def add_item(self, widget):
        if not isinstance(widget, list):
            widget = [widget]
        for _w in widget:
            self.add_items.append(_w)
            self.scene().addItem(_w)

    def remove_item(self, widget):
        if not isinstance(widget, list):
            widget = [widget]
        for _w in widget:
            self.add_items.remove(_w)
            self.scene().removeItem(_w)

    def clear(self):
        self.scene().clear()
        self.add_items = []

    def _delete(self):
        for _n in self.scene().selectedItems():
            _n.delete()



# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
