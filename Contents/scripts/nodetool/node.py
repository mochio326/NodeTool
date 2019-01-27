# -*- coding: utf-8 -*-
from .vendor.Qt import QtCore, QtGui, QtWidgets
from . import port


class NodeLabel(QtWidgets.QGraphicsItem):

    @property
    def node(self):
        return self.parentItem()

    def __init__(self, parent, label):
        super(NodeLabel, self).__init__(parent)
        self.rect = QtCore.QRect(0, 0, self.node.width, 20)
        self.label = label
        # Pen.
        self.pen = QtGui.QPen()
        self.pen.setStyle(QtCore.Qt.SolidLine)
        self.pen.setWidth(1)
        self.pen.setColor(QtGui.QColor(200, 200, 200, 255))

        self.brush = QtGui.QLinearGradient(0, 0, self.node.width, 0)
        self.brush.setColorAt(0.0, QtGui.QColor(68, 160, 122))
        self.brush.setColorAt(1.0, QtGui.QColor(60, 60, 60, 255))

    def paint(self, painter, option, widget):
        painter.setBrush(self.brush)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawPath(self.shape())

        painter.setPen(self.pen)
        painter.setFont(QtGui.QFont('Decorative', 10))
        rect = self.boundingRect()
        rect.moveTop(rect.y() - 2)
        painter.drawText(rect, QtCore.Qt.AlignCenter, self.label)

    def boundingRect(self):
        rect = QtCore.QRect(0, 0, self.node.width, 20)
        return QtCore.QRectF(rect)

    def shape(self):
        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(1, 1, self.node.width - 2, 19), 9, 9)
        path2 = QtGui.QPainterPath()
        path2.addPolygon(QtCore.QRectF(1, 10, self.node.width - 2, 10))
        path3 = path.united(path2)
        return path3


class Node(QtWidgets.QGraphicsItem):
    TYPE = 'Node'
    DEF_Z_VALUE = 0.1

    @property
    def rect(self):
        return QtCore.QRect(0, 0, self.width, self.height)

    @property
    def ports(self):
        return [_item for _item in self.childItems() if isinstance(_item, port.Port)]

    def __init__(self, name='', width=140, height=60, label='node'):
        super(Node, self).__init__()
        self.name = name
        self.setZValue(self.DEF_Z_VALUE)
        self.width = width
        self.height = height

        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)

        # Brush.
        self.brush = QtGui.QBrush()
        self.brush.setStyle(QtCore.Qt.SolidPattern)
        self.brush.setColor(QtGui.QColor(60, 60, 60, 255))

        # Pen.
        self.pen = QtGui.QPen()
        self.pen.setStyle(QtCore.Qt.SolidLine)
        self.pen.setWidth(1)
        self.pen.setColor(QtGui.QColor(140, 140, 140, 255))

        self.sel_pen = QtGui.QPen()
        self.sel_pen.setStyle(QtCore.Qt.SolidLine)
        self.sel_pen.setWidth(1)
        self.sel_pen.setColor(QtGui.QColor(0, 255, 255, 255))

        if label is not None:
            NodeLabel(self, label)
            self.port_init_y = 30
        else:
            self.port_init_y = 10

    def add_port(self, port_type, color, value_type, label):
        _y = self.port_init_y + 20 * len(self.ports)
        p = port.Port(self, port_type, color, value_type, _y, label)
        self.height = _y + 25
        self.update()
        return p

    def shape(self):
        path = QtGui.QPainterPath()
        path.addRect(self.boundingRect())
        return path

    def boundingRect(self):
        return QtCore.QRectF(self.rect)

    def paint(self, painter, option, widget):
        painter.setBrush(self.brush)
        if self.isSelected():
            painter.setPen(self.sel_pen)
        else:
            painter.setPen(self.pen)
        painter.drawRoundedRect(self.rect, 10.0, 10.0)

    def mousePressEvent(self, event):
        # 自身と関連するラインを見やすくするために最前面表示
        self.setZValue(100.0)
        for _p in self.ports:
            for _l in _p.lines:
                _l.setZValue(100.0)
        super(Node, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super(Node, self).mouseMoveEvent(event)
        # 自身以外も選択されている場合にまとめて処理する
        for _n in self.scene().selectedItems():
            for _p in _n.ports:
                _p.update_connect_line_pos()

    def get_scene_nodes(self):
        # シーン内のノードのみ取得
        for _i in self.scene().items():
            if not isinstance(_i, self.__class__):
                continue
            yield _i

    def mouseReleaseEvent(self, event):
        # ノードを現在の描画順を維持したまま数値を整頓
        node_z_list = []
        for _n in self.get_scene_nodes():
            node_z_list.append([_n.zValue(), _n])
        node_z_list = sorted(node_z_list, key=lambda x:x[0])
        for _i, _n in enumerate(node_z_list):
            _n[1].setZValue(self.DEF_Z_VALUE + 0.01 * _i)
        # ラインは最後面に戻しとく
        for _p in self.ports:
            for _l in _p.lines:
                _l.setZValue(_l.DEF_Z_VALUE)
        super(Node, self).mouseReleaseEvent(event)

    def delete(self):
        for _p in self.ports:
            for _l in _p.lines:
                _l.delete()
        self.scene().removeItem(self)

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu()
        make = menu.addAction('make')
        makeFromHere = menu.addAction('make from here')
        debugConnections = menu.addAction('debug connections')
        selectedAction = menu.exec_(event.screenPos())

        if selectedAction == debugConnections:
            print 'input_port'
            for idx, line in enumerate(self.input_port.lines):
                print '  Line {0}'.format(idx)
                print '    point_a: {0}'.format(line.point_a)
                print '    point_b: {0}'.format(line.point_b)
            print 'output_port'
            for idx, line in enumerate(self.output_port.lines):
                print '  Line {0}'.format(idx)
                print '    point_a: {0}'.format(line.point_a)
                print '    point_b: {0}'.format(line.point_b)

# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
