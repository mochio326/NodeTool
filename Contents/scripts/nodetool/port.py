# -*- coding: utf-8 -*-
from .vendor.Qt import QtCore, QtGui, QtWidgets
from . import line


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
            label_x = port_item.PORT_SIZE + 2
        else:
            self.text_align = QtCore.Qt.AlignRight
            label_x = node_item.width - width - port_item.PORT_SIZE

        return QtCore.QRect(label_x, 0 - self.text_size / 2, width, height)

    def shape(self):
        path = QtGui.QPainterPath()
        path.addEllipse(self.boundingRect())
        return path

    def mousePressEvent(self, event):
        print self.label


class Port(QtWidgets.QGraphicsItem):
    PORT_SIZE = 12
    INTERVAL_SIZE = 25

    @property
    def node(self):
        return self.parentItem()

    def __init__(self, parent, port_type=None, color=None, value_type=None, label=None):
        super(Port, self).__init__(parent)
        self.setAcceptHoverEvents(True)
        self.color = color
        self.value_type = value_type
        self.hover_port = None
        self.type = port_type
        self.new_line = None
        self.children_port_open = False

        if isinstance(parent, Port):
            rect_x = parent.rect.x()
            self.type = parent.type

        else:
            if self.type == 'in':
                rect_x = 0 - self.PORT_SIZE / 2
            else:
                rect_x = parent.width - self.PORT_SIZE / 2

        self.rect = QtCore.QRect(rect_x, 0, 12, 12)

        if label is not None:
            PortLabel(self, label)

        # Brush.
        self.brush = QtGui.QBrush()
        self.brush.setStyle(QtCore.Qt.SolidPattern)
        self.brush.setColor(QtCore.Qt.red)

        # Pen.
        self.pen = QtGui.QPen()
        self.pen.setStyle(QtCore.Qt.SolidLine)
        self.pen.setWidth(2)
        self.pen.setColor(self.color)

        # line.Lines.
        self.new_lines = None
        self.lines = []

    def setY(self, value):
        super(self.__class__, self).setY(value)

    def shape(self):
        path = QtGui.QPainterPath()
        path.addEllipse(self.boundingRect())
        return path

    @property
    def children_port(self):
        return [_item for _item in self.childItems() if isinstance(_item, Port)]

    def deploying_port(self):
        #if not self.children_port_open:
        #    return
        _port_y = self.INTERVAL_SIZE
        for _p in self.children_port:
            _p.setY(_port_y)
            _port_y = _port_y + self.INTERVAL_SIZE + len(_p.children_port) * self.INTERVAL_SIZE
            _p.deploying_port()

    @property
    def height_space(self):
        if not self.children_port_open:
            return self.INTERVAL_SIZE


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
        if self.isUnderMouse():
            self.change_to_hover_color()

    def hoverEnterEvent(self, event):
        pass

    def hoverLeaveEvent(self, event):
        self.change_to_basic_color()

    def change_to_hover_color(self):
        self.pen.setColor(QtGui.QColor(255, 200, 200, 255))
        self.brush.setColor(QtGui.QColor(180, 120, 190, 255))
        self.update()

    def change_to_basic_color(self):
        self.pen.setColor(self.color)
        self.brush.setColor(QtGui.QColor(180, 20, 90, 255))
        self.update()

    def mousePressEvent(self, event):
        self.hover_port = None

        if self.type == 'out':
            point_a = self.get_center()
            point_b = self.mapToScene(event.pos())

        elif self.type == 'in':
            point_a = self.mapToScene(event.pos())
            point_b = self.get_center()

        self.new_line = line.Line(point_a, point_b, self.color)
        self.scene().addItem(self.new_line)
        self.connect(self.new_line, True)

    def mouseMoveEvent(self, event):
        self.new_line.mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.new_line.mouseReleaseEvent(event)

    def disconnect(self, line_):
        if line_ not in self.lines:
            return

        if self.type == 'in':
            line_.target = None
        else:
            line_.source = None
        self.lines.remove(line_)
        if self.node.TYPE == 'Pin':
            self.node.return_initial_state()
        self.update()

    def connect(self, line_, not_del=False):
        if self.type == 'in':
            if len(self.lines) > 0 and not not_del:
                _l = self.lines[0]
                _l.delete()
                self.lines = []
            line_.target = self
            line_.point_b = self.get_center()
        else:
            line_.source = self
            line_.point_a = self.get_center()
        if not not_del:
            self.lines.append(line_)
        self.update()

    def get_center(self):
        center = QtCore.QPointF(self.rect.x() + self.rect.width() / 2, self.rect.y() + self.rect.height() / 2)
        return self.mapToScene(center)

    def can_connection(self, port):
        if self.value_type != port.value_type:
            # Noneな場合はPinなので例外
            if self.value_type is not None and port.value_type is not None:
                return False
        if self.type == port.type:
            return False
        # サイクル確認
        # memo:ラインをたどって全体的にサイクルしてないかを調べる予定
        if self.node == port.node:
            return False
        return True

    def update_connect_line_pos(self):
        if self.type == 'in':
            _p = 'point_b'
        else:
            _p = 'point_a'
        for _l in self.lines:
            setattr(_l, _p, self.get_center())
        for cp in self.children_port:
            cp.update_connect_line_pos()

# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
