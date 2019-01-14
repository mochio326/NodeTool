# -*- coding: utf-8 -*-
from .vendor.Qt import QtCore, QtGui, QtWidgets
from .line import Line


class PortLabel(QtWidgets.QGraphicsItem):

    @property
    def port(self):
        return self.parentItem()

    def __init__(self, parent, label):
        super(PortLabel, self).__init__(parent)
        self.label = label
        self.text_size = 10

        # Pen.
        self.pen = QtGui.QPen()
        self.pen.setStyle(QtCore.Qt.SolidLine)
        self.pen.setWidth(2)
        self.pen.setColor(QtGui.QColor(200, 200, 200, 255))

    def paint(self, painter, option, widget):
        painter.setPen(self.pen)

        painter.setFont(self.font)
        painter.drawText(self.boundingRect(), self.text_align, self.label)

    @property
    def font(self):
        return QtGui.QFont('Decorative', self.text_size)

    def boundingRect(self):
        node_item = self.port.node
        port_item = self.port

        font_metrics = QtGui.QFontMetrics(self.font)
        width = font_metrics.width(self.label)
        height = font_metrics.height()
        # ベースラインから下降サイズを無視する
        # こういう場合、height()ではなく、ascent()を使ってもOK!
        height = height - font_metrics.descent()

        if self.port.type == 'in':
            self.text_align = QtCore.Qt.AlignLeft
            label_x = port_item.port_size + 2
        else:
            self.text_align = QtCore.Qt.AlignRight
            label_x = node_item.width - width - port_item.port_size

        return QtCore.QRect(label_x, port_item.position_y - self.text_size / 2, width, height)

    def shape(self):
        path = QtGui.QPainterPath()
        path.addEllipse(self.boundingRect())
        return path

    def mousePressEvent(self, event):
        print self.label


class Port(QtWidgets.QGraphicsItem):

    @property
    def node(self):
        return self.parentItem()

    def __init__(self, parent, port_type, color, value_type, position_y=30, label=None):
        super(Port, self).__init__(parent)
        self.setAcceptHoverEvents(True)
        self.color = color
        self.value_type = value_type
        self.port_size = 12
        self.hover_port = None
        self.type = port_type
        self.position_y = position_y
        self.new_line = None

        if self.type == 'in':
            rect_x = 0 - self.port_size / 2
        else:
            rect_x = parent.width - self.port_size / 2
        self.rect = QtCore.QRect(rect_x, self.position_y, 12, 12)

        if label is not None:
            PortLabel(self, self.type)

        # Brush.
        self.brush = QtGui.QBrush()
        self.brush.setStyle(QtCore.Qt.SolidPattern)
        self.brush.setColor(QtCore.Qt.red)

        # Pen.
        self.pen = QtGui.QPen()
        self.pen.setStyle(QtCore.Qt.SolidLine)
        self.pen.setWidth(2)
        self.pen.setColor(self.color)

        # Lines.
        self.new_lines = None
        self.lines = []

    def shape(self):
        path = QtGui.QPainterPath()
        path.addEllipse(self.boundingRect())
        return path

    def boundingRect(self):
        return QtCore.QRectF(self.rect.x() - 5.0, self.rect.y() - 5.0, self.rect.width() + 5.0,
                             self.rect.height() + 5.0)

    def paint(self, painter, option, widget):
        if len(self.lines) == 0:
            self.brush.setColor(QtGui.QColor(60, 60, 60, 255))
        else:
            self.brush.setColor(self.color)
        painter.setBrush(self.brush)
        painter.setPen(self.pen)
        painter.drawEllipse(self.rect)

    def hoverMoveEvent(self, event):
        # Do your stuff here.
        pass

    def hoverEnterEvent(self, event):
        self.pen.setColor(QtGui.QColor(255, 200, 200, 255))
        self.brush.setColor(QtGui.QColor(180, 120, 190, 255))
        self.update()

    def hoverLeaveEvent(self, event):
        self.pen.setColor(self.color)
        self.brush.setColor(QtGui.QColor(180, 20, 90, 255))
        self.update()

    def mousePressEvent(self, event):
        self.hover_port = None

        if self.type == 'out':
            rect = self.boundingRect()
            point_a = QtCore.QPointF(rect.x() + rect.width() / 2, rect.y() + rect.height() / 2)
            point_a = self.mapToScene(point_a)
            point_b = self.mapToScene(event.pos())
            self.new_line = Line(point_a, point_b, self.color)
            self.scene().addItem(self.new_line)
            self.new_line.moving = 'b'
            self.new_line.source = self

        elif self.type == 'in':
            rect = self.boundingRect()
            point_a = self.mapToScene(event.pos())
            point_b = QtCore.QPointF(rect.x() + rect.width() / 2, rect.y() + rect.height() / 2)
            point_b = self.mapToScene(point_b)
            self.new_line = Line(point_a, point_b, self.color)
            self.scene().addItem(self.new_line)
            self.new_line.moving = 'a'
            self.new_line.target = self

        else:
            super(Port, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.new_line.mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        pos = event.scenePos().toPoint()
        item = self.scene().itemAt(pos.x(), pos.y(), QtGui.QTransform())

        # ポート以外で離した
        if not isinstance(item, Port):
            self.delete_new_line(event)
            return

        # 同じ側のピンの場合
        if self.type == item.type:
            self.delete_new_line(event)
            return

        # サイクル確認
        # memo:ラインをたどって全体的にサイクルしてないかを調べる
        if item.node == self.node:
            self.delete_new_line(event)
            return

        # 相手がPINの場合
        if item.node.TYPE == 'Pin':
            item.node.propagate(self, item, self.new_line)

        # 自分がPINの場合
        if self.node.TYPE == 'Pin':
            self.node.propagate(item, self, self.new_line)

        if self.value_type != item.value_type:
            self.delete_new_line(event)
            return

        if self.type == 'out' and item.type == 'in':
            self.new_line.source = self
            self.new_line.target = item
            # 接続先に既に接続済みのラインがあったら削除
            item.delete_old_line()
            item.lines.append(self.new_line)
            self.lines.append(self.new_line)
            self.new_line.point_b = item.get_center()
        elif self.type == 'in' and item.type == 'out':
            # 自身のポートに既に接続済みのラインがあったら削除
            self.delete_old_line()
            self.new_line.source = item
            self.new_line.target = self
            item.lines.append(self.new_line)
            self.lines.append(self.new_line)
            self.new_line.point_a = item.get_center()

    def delete_new_line(self, event):
        self.scene().removeItem(self.new_line)
        self.new_line = None
        super(Port, self).mouseReleaseEvent(event)
        return

    def remove_old_line(self):
        # 既に接続済みのラインがあったら接続を解除。ラインは消さない
        if len(self.lines) > 0:
            line = self.lines[0]
            _target = line.target
            _target.lines.remove(line)
            self.lines = []
            self.update()

    def delete_old_line(self):
        # 既に接続済みのラインがあったら存在ごと削除
        if len(self.lines) > 0:
            line = self.lines[0]
            _target = line.target
            _source = line.source
            _target.lines.remove(line)
            _source.lines.remove(line)
            self.lines = []
            self.scene().removeItem(line)
            self.update()

    def get_center(self):
        rect = self.boundingRect()
        center = QtCore.QPointF(rect.x() + rect.width() / 2, rect.y() + rect.height() / 2)
        center = self.mapToScene(center)
        return center

# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
