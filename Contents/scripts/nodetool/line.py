# -*- coding: utf-8 -*-
from .vendor.Qt import QtCore, QtGui, QtWidgets
import cmath


class LineArrow(QtWidgets.QGraphicsItem):
    def __init__(self, parent, color):
        super(LineArrow, self).__init__(parent)
        self.triangle = QtGui.QPolygon()
        self.color = color

        # Pen.
        self.pen = QtGui.QPen()
        self.pen.setStyle(QtCore.Qt.SolidLine)
        self.pen.setWidth(0)
        self.pen.setColor(self.color)

    @property
    def line(self):
        return self.parentItem()

    def paint(self, painter, option, widget):
        painter.setPen(self.pen)
        path = QtGui.QPainterPath()
        dx = self.line.point_b.x() - self.line.point_a.x()
        dy = self.line.point_b.y() - self.line.point_a.y()
        triangle_x = (self.line.point_a.x() + self.line.point_b.x()) / 2
        triangle_y = (self.line.point_a.y() + self.line.point_b.y()) / 2
        # パスの接線をパスの描画とは切り離して調整しないとうまいこと回転できなかった
        if dx > 0:
            ctrl1_dummy = QtCore.QPointF(self.line.point_a.x() + dx * 0.3,
                                         self.line.point_a.y() + dy * 0.1)
            ctrl2_dummy = QtCore.QPointF(self.line.point_b.x() - dx * 0.3,
                                         self.line.point_a.y() + dy * 0.9)
        else:
            ctrl1_dummy = QtCore.QPointF(self.line.point_a.x() + abs(dx * 0.7),
                                         self.line.point_a.y() + dy * 0.1)
            ctrl2_dummy = QtCore.QPointF(self.line.point_b.x() - abs(dx * 0.7),
                                         self.line.point_a.y() + dy * 0.9)

        # 三角形の中心からの先端へのベクトル
        line_vector_x = ctrl1_dummy.x() - ctrl2_dummy.x()
        line_vector_y = ctrl1_dummy.y() - ctrl2_dummy.y()
        line_vector = complex(line_vector_x, line_vector_y)
        # 単位ベクトルに変換
        _p = cmath.phase(line_vector)
        line_vector = cmath.rect(1, _p)

        #
        triangle_points = [complex(-5, 0),
                           complex(5, 7),
                           complex(5, -7),
                           complex(-5, 0)]
        triangle_points = [_p * line_vector for _p in triangle_points]
        triangle_points = [QtCore.QPoint(triangle_x + _p.real, triangle_y + _p.imag) for _p in triangle_points]
        self.triangle = QtGui.QPolygon(triangle_points)
        path.addPolygon(self.triangle)
        painter.fillPath(path, self.pen.color())
        painter.drawPath(path)

    def boundingRect(self):
        return self.triangle.boundingRect()

    def shape(self):
        path = QtGui.QPainterPath()
        path.addEllipse(self.boundingRect())
        return path


class Line(QtWidgets.QGraphicsPathItem):

    def __init__(self, point_a, point_b, color):
        from .port import Port
        self.port = Port

        super(Line, self).__init__()
        self.color = color
        self._point_a = point_a
        self._point_b = point_b
        self._source = None
        self._target = None
        self.moving = None
        self.pen = QtGui.QPen()
        self.pen.setStyle(QtCore.Qt.SolidLine)
        self.pen.setWidth(1)
        self.pen.setColor(self.color)
        self.hover_port = None
        self.arrow = LineArrow(self, self.color)

        self.setZValue(-1)
        self.setBrush(QtCore.Qt.NoBrush)
        self.setPen(self.pen)
        self.setAcceptHoverEvents(True)

    def mousePressEvent(self, event):
        self.point_b = event.pos()
        self.moving = 'b'

    def mouseMoveEvent(self, event):
        pos = event.scenePos().toPoint()
        setattr(self, 'point_{0}'.format(self.moving), pos)

        if self.moving == 'a':
            none_move_port = self.target
        else:
            none_move_port = self.source

        # ポートのハイライト
        pos = event.scenePos().toPoint()
        item = self.scene().itemAt(pos.x(), pos.y(), QtGui.QTransform())

        if isinstance(item, self.port):
            if none_move_port.value_type == item.value_type and none_move_port.type != item.type:
                self.hover_port = item
                self.hover_port.hoverEnterEvent(None)
                self.hover_port.update()
        else:
            if self.hover_port is not None:
                self.hover_port.hoverLeaveEvent(None)
                self.hover_port.update()
                self.hover_port = None

    def mouseReleaseEvent(self, event):
        pos = event.scenePos().toPoint()
        item = self.scene().itemAt(pos.x(), pos.y(), QtGui.QTransform())

        # ポート以外で離したらラインごと削除
        if not isinstance(item, self.port):
            self.target.delete_old_line()

            # PINの見た目の初期化
            if self.target.node.TYPE == 'Pin':
                self.target.node.return_initial_state()
            if self.source.node.TYPE == 'Pin':
                self.source.node.return_initial_state()
            return

        if self.source.value_type != item.value_type or self.source.type == item.type:
            self.point_b = self.target.get_center()
            return

        if item.type == 'in':
            # 古いポート側から削除
            self.target.remove_old_line()
            # 新しいポート側に追加
            self.target = item
            self.target.delete_old_line()
            self.target.lines.append(self)
            self.point_b = self.target.get_center()

    def updatePath(self):
        path = QtGui.QPainterPath()
        path.moveTo(self.point_a)
        dx = self.point_b.x() - self.point_a.x()
        dy = self.point_b.y() - self.point_a.y()
        ctrl1 = QtCore.QPointF(self.point_a.x() + abs(dx * 0.7), self.point_a.y() + dy * 0.1)
        ctrl2 = QtCore.QPointF(self.point_b.x() - abs(dx * 0.7), self.point_a.y() + dy * 0.9)
        path.cubicTo(ctrl1, ctrl2, self.point_b)
        self.setPath(path)

    def hoverMoveEvent(self, event):
        # Do your stuff here.
        pass

    def hoverEnterEvent(self, event):
        self.pen.setColor(QtGui.QColor(255, 200, 200, 255))
        self.arrow.pen.setColor(QtGui.QColor(255, 200, 200, 255))
        self.setPen(self.pen)

    def hoverLeaveEvent(self, event):
        self.pen.setColor(self.color)
        self.arrow.pen.setColor(self.color)
        self.setPen(self.pen)

    def paint(self, painter, option, widget):
        painter.setPen(self.pen)
        painter.drawPath(self.path())
        self.arrow.paint(painter, option, widget)

    @property
    def point_a(self):
        return self._point_a

    @point_a.setter
    def point_a(self, point):
        self._point_a = point
        self.updatePath()

    @property
    def point_b(self):
        return self._point_b

    @point_b.setter
    def point_b(self, point):
        self._point_b = point
        self.updatePath()

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, widget):
        self._source = widget

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, widget):
        self._target = widget

# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
