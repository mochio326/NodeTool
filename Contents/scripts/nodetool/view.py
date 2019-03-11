# -*- coding: utf-8 -*-
from .vendor.Qt import QtCore, QtGui, QtWidgets
import uuid
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
        self._operation_history = [None]
        self._current_operation_history = 0

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
                self.create_history()
                return
            if event.key() == QtCore.Qt.Key_X:
                # self._cut()
                print 'cut'
                return
            if event.key() == QtCore.Qt.Key_Z:
                self._undo_redo_base('undo')
                print 'undo'
                return
            if event.key() == QtCore.Qt.Key_Y:
                print 'redo'
                self._undo_redo_base('redo')
                return
        if event.key() == QtCore.Qt.Key_A:
            _bbox = self.scene().itemsBoundingRect()
            _pos = self.mapToScene(_bbox.x(), _bbox.y())
            self.translate(_pos.x(), _pos.y())

            return

        if event.key() == QtCore.Qt.Key_Delete:
            self._delete()
            self.create_history()
            return

    def add_node_on_center(self, node, history=True):
        self.add_item(node)
        _pos = self.mapToScene(self.width() / 2, self.height() / 2)
        node.setPos(_pos)
        node.port_expanded.connect(self.create_history)
        node.pos_changed.connect(self.create_history)
        node.port_connect_changed.connect(self.create_history)
        if history:
            self.create_history()

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
        self._clipboard = {}
        self._paste_offset = 0
        selected_nodes = self.scene().selectedItems()
        related_lines = common.get_lines_related_with_node(selected_nodes, self)
        self._clipboard = common.get_save_data(selected_nodes, related_lines)

    def _paste(self):
        if self._clipboard is None:
            return
        self._paste_offset = self._paste_offset + 1
        # common.refresh_all_node_id_in_scene(self)

        id_change_dict = {}
        for _n in self._clipboard['node']:
            new_id = str(uuid.uuid4())
            id_change_dict[_n['id']] = new_id
            _n['id'] = new_id
            _n['z_value'] = _n['z_value'] + self._paste_offset
            _n['x'] = _n['x'] + self._paste_offset * 10
            _n['y'] = _n['y'] + self._paste_offset * 10
        for _l in self._clipboard['line']:
            if id_change_dict.get(_l['source']['node_id']) is not None:
                _l['source']['node_id'] = id_change_dict.get(_l['source']['node_id'])
            if id_change_dict.get(_l['target']['node_id']) is not None:
                _l['target']['node_id'] = id_change_dict.get(_l['target']['node_id'])

        nodes = common.load_save_data(self._clipboard, self)
        self.scene().clearSelection()
        for _n in nodes:
            _n.setSelected(True)
        self.scene().update()

    def create_history(self):
        data = common.get_save_data_from_scene_all(self)
        # Undo Redo用の操作
        if self._current_operation_history > 0:
            del self._operation_history[0:self._current_operation_history]
        self._operation_history.insert(0, data)
        self._current_operation_history = 0

    def _undo_redo_base(self, type_):
        _add = 1 if type_ == 'undo' else -1
        if self._current_operation_history >= len(self._operation_history) - _add:
            return
        if self._current_operation_history + _add < 0:
            return
        self._current_operation_history = self._current_operation_history + _add
        data = self._operation_history[self._current_operation_history]
        self.clear()
        common.load_save_data(data, self)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
