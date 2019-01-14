# -*- coding: utf-8 -*-
from .vendor.Qt import QtCore, QtGui, QtWidgets
from .port import Port


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

    @property
    def rect(self):
        return QtCore.QRect(0, 0, self.width, self.height)

    def __init__(self, width=140, height=60, label='node'):
        super(Node, self).__init__()
        self.width = width
        self.height = height
        self.ports = []

        self.name = None
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
        _s = Port(self, port_type, color, value_type, _y, label)
        self.ports.append(_s)

        self.height = _y + 25
        self.update()

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

    def mouseMoveEvent(self, event):
        super(Node, self).mouseMoveEvent(event)
        # 自身以外も選択されている場合にまとめて処理する
        for _n in self.scene().selectedItems():
            for _s in _n.ports:
                for line in _s.lines:
                    if _s.type == 'out':
                        line.point_a = line.source.get_center()
                        line.point_b = line.target.get_center()
                    if _s.type == 'in':
                        line.point_a = line.source.get_center()
                        line.point_b = line.target.get_center()

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
