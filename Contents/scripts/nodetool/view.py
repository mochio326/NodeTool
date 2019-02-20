# -*- coding: utf-8 -*-
from .vendor.Qt import QtCore, QtGui, QtWidgets
import copy
from . import common

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
            delta = (self.mapToScene(event.pos()) - self.mapToScene(self.prev_pos)) * -1.0
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

        if event.button() == QtCore.Qt.RightButton:
            menu = QtWidgets.QMenu()
            save = menu.addAction('save')
            load = menu.addAction('load')
            selectedAction = menu.exec_(event.globalPos())

            if selectedAction == save:
                common.scene_save(self)
            if selectedAction == load:
                common.scene_load(self)


    def keyPressEvent(self, event):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            if event.key() == QtCore.Qt.Key_C:
                self._copy()
                return
            if event.key() == QtCore.Qt.Key_V:
                self._paste()
                return
            if event.key() == QtCore.Qt.Key_X:
                # self._cut()
                print 'cut'
                return
            if event.key() == QtCore.Qt.Key_Z:
                # self._undo()
                print 'undo'
                return
            if event.key() == QtCore.Qt.Key_Y:
                print 'redo'
                # self._redo()
                return
        if event.key() == QtCore.Qt.Key_A:
            print 'a'
            _bbox = self.scene().itemsBoundingRect()
            print _bbox.x(), _bbox.y()
            _pos = self.mapToScene(_bbox.x(), _bbox.y() )

            self.translate(_pos.x(), _pos.y())

            return

        if event.key() == QtCore.Qt.Key_Delete:
            self._delete()
            return

    def add_item_on_center(self, widget):
        self.add_item(widget)
        _pos = self.mapToScene(self.width() / 2, self.height() / 2)
        widget.setPos(_pos)

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

    def _copy(self):
        self._clipboard = []
        for _n in self.scene().selectedItems():
            self._clipboard.append(_n.save_data)
        selected_nodes_id = [_n.id for _n in self.scene().selectedItems()]
        for _i in self.scene().items():
            if isinstance(_i, ):
                aaa

    def _paste(self):
        if self._clipboard is None:
            return
        for _c in self._clipboard:
            box = common.create_node_for_xml(_c['name'])
            self.add_item_on_center(box)
            common.load_node_data(box, _c, True)

        self.scene().update()

# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
