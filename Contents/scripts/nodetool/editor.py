# -*- coding: utf-8 -*-
from .vendor.Qt import QtCore, QtGui, QtWidgets
import math
import cmath

'''
============================================================
---   IMPORT MODULES
============================================================
'''
import maya.OpenMayaUI as OpenMayaUI
from shiboken2 import wrapInstance

'''
============================================================
---   GRAPHICS CLASSES
============================================================
'''

class NodeLineArrow(QtWidgets.QGraphicsItem):
    def __init__(self, parent):
        super(NodeLineArrow, self).__init__(parent)
        self.triangle = QtGui.QPolygon()

        # Pen.
        self.pen = QtGui.QPen()
        self.pen.setStyle(QtCore.Qt.SolidLine)
        self.pen.setWidth(0)
        self.pen.setColor(QtCore.Qt.red)

    def paint(self, painter, option, widget):
        painter.setPen(self.pen)
        path = QtGui.QPainterPath()
        dx = self.parentItem().point_b.x() - self.parentItem().point_a.x()
        dy = self.parentItem().point_b.y() - self.parentItem().point_a.y()
        triangle_x = (self.parentItem().point_a.x() + self.parentItem().point_b.x()) / 2
        triangle_y = (self.parentItem().point_a.y() + self.parentItem().point_b.y()) / 2
        # パスの接線をパスの描画とは切り離して調整しないとうまいこと回転できなかった
        if dx > 0:
            ctrl1_dummy = QtCore.QPointF(self.parentItem().point_a.x() + dx * 0.3, self.parentItem().point_a.y() + dy * 0.1)
            ctrl2_dummy = QtCore.QPointF(self.parentItem().point_b.x() - dx * 0.3, self.parentItem().point_a.y() + dy * 0.9)
        else:
            ctrl1_dummy = QtCore.QPointF(self.parentItem().point_a.x() + abs(dx * 0.7), self.parentItem().point_a.y() + dy * 0.1)
            ctrl2_dummy = QtCore.QPointF(self.parentItem().point_b.x() - abs(dx * 0.7), self.parentItem().point_a.y() + dy * 0.9)

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
        painter.fillPath(path, QtCore.Qt.red)
        painter.drawPath(path)

    def boundingRect(self):
        return self.triangle.boundingRect()

    def shape(self):
        path = QtGui.QPainterPath()
        path.addEllipse(self.boundingRect())
        return path


class NodeLine(QtWidgets.QGraphicsPathItem):
    def __init__(self, point_a, point_b):
        super(NodeLine, self).__init__()
        self._point_a = point_a
        self._point_b = point_b
        self._source = None
        self._target = None
        self.setZValue(-1)
        self.setBrush(QtCore.Qt.NoBrush)
        self.pen = QtGui.QPen()
        self.pen.setStyle(QtCore.Qt.SolidLine)
        self.pen.setWidth(1)
        self.pen.setColor(QtGui.QColor(255, 20, 20, 255))
        self.setPen(self.pen)
        self.setAcceptHoverEvents(True)
        self.hover_socket = None
        self.arrow = NodeLineArrow(self)

    def mousePressEvent(self, event):
        self.point_b = event.pos()

    def mouseMoveEvent(self, event):
        self.point_b = event.pos()

        # ソケットのハイライト
        pos = event.scenePos().toPoint()
        item = self.scene().itemAt(pos.x(), pos.y(), QtGui.QTransform())
        if isinstance(item, NodeSocket):
            self.hover_socket = item
            self.hover_socket.hoverEnterEvent(None)
            self.hover_socket.update()
        else:
            if self.hover_socket is not None:
                self.hover_socket.hoverLeaveEvent(None)
                self.hover_socket.update()
                self.hover_socket = None

    def mouseReleaseEvent(self, event):
        pos = event.scenePos().toPoint()
        item = self.scene().itemAt(pos.x(), pos.y(), QtGui.QTransform())
        if item.type == 'in':
            # 古いポート側から削除
            self.target.remove_old_in_line()
            # 新しいポート側に追加
            self.target = item
            self.target.delete_old_in_line()
            self.target.in_lines.append(self)
            self.point_b = self.target.get_center()
        else:
            # ソケット以外で離したらラインごと削除
            self.target.delete_old_in_line()

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
        self.setPen(self.pen)

    def hoverLeaveEvent(self, event):
        self.pen.setColor(QtGui.QColor(255, 20, 20, 255))
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


class NodeLabel(QtWidgets.QGraphicsItem):
    def __init__(self, rect, parent):
        super(NodeLabel, self).__init__(parent)
        self.rect = rect

        # Pen.
        self.pen = QtGui.QPen()
        self.pen.setStyle(QtCore.Qt.SolidLine)
        self.pen.setWidth(2)
        self.pen.setColor(QtGui.QColor(200, 200, 200, 255))

    def paint(self, painter, option, widget):
        painter.setPen(self.pen)
        # painter.drawEllipse(self.rect)
        painter.setFont(QtGui.QFont('Decorative', 10))
        painter.drawText(self.boundingRect(), QtCore.Qt.AlignLeft, 'node')

    def boundingRect(self):
        return QtCore.QRectF(self.rect)

    def shape(self):
        path = QtGui.QPainterPath()
        path.addEllipse(self.boundingRect())
        return path


class NodeSocket(QtWidgets.QGraphicsItem):
    def __init__(self, rect, parent, socket_type):
        super(NodeSocket, self).__init__(parent)
        self.setAcceptHoverEvents(True)

        self.hover_socket = None
        self.rect = rect
        self.type = socket_type

        # Brush.
        self.brush = QtGui.QBrush()
        self.brush.setStyle(QtCore.Qt.SolidPattern)
        self.brush.setColor(QtCore.Qt.red)

        # Pen.
        self.pen = QtGui.QPen()
        self.pen.setStyle(QtCore.Qt.SolidLine)
        self.pen.setWidth(3)
        self.pen.setColor(QtCore.Qt.red)

        # Lines.
        self.new_lines = None
        self.out_lines = []
        self.in_lines = []

    def shape(self):
        path = QtGui.QPainterPath()
        path.addEllipse(self.boundingRect())
        return path

    def boundingRect(self):
        return QtCore.QRectF(self.rect)

    def paint(self, painter, option, widget):
        line_count = 0
        if self.type == 'out':
            line_count = len(self.out_lines)
        elif self.type == 'in':
            line_count = len(self.in_lines)

        if line_count == 0:
            self.brush.setColor(QtGui.QColor(60, 60, 60, 255))
        else:
            self.brush.setColor(QtCore.Qt.red)
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
        self.pen.setColor(QtGui.QColor(255, 20, 20, 255))
        self.brush.setColor(QtGui.QColor(180, 20, 90, 255))
        self.update()

    def mousePressEvent(self, event):
        self.hover_socket = None

        if self.type == 'out':
            rect = self.boundingRect()
            point_a = QtCore.QPointF(rect.x() + rect.width() / 2, rect.y() + rect.height() / 2)
            point_a = self.mapToScene(point_a)
            point_b = self.mapToScene(event.pos())
            self.new_line = NodeLine(point_a, point_b)
            self.scene().addItem(self.new_line)
        elif self.type == 'in':
            rect = self.boundingRect()
            point_a = self.mapToScene(event.pos())
            point_b = QtCore.QPointF(rect.x() + rect.width() / 2, rect.y() + rect.height() / 2)
            point_b = self.mapToScene(point_b)
            self.new_line = NodeLine(point_a, point_b)
            self.scene().addItem(self.new_line)
        else:
            super(NodeSocket, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.type == 'out':
            point_b = self.mapToScene(event.pos())
            self.new_line.point_b = point_b
        elif self.type == 'in':
            point_a = self.mapToScene(event.pos())
            self.new_line.point_a = point_a
        else:
            super(NodeSocket, self).mouseMoveEvent(event)

        pos = event.scenePos().toPoint()
        item = self.scene().itemAt(pos.x(), pos.y(), QtGui.QTransform())
        if isinstance(item, NodeSocket):
            self.hover_socket = item
            self.hover_socket.hoverEnterEvent(None)
            self.hover_socket.update()
        else:
            if self.hover_socket is not None:
                self.hover_socket.hoverLeaveEvent(None)
                self.hover_socket.update()
                self.hover_socket = None

    def mouseReleaseEvent(self, event):
        pos = event.scenePos().toPoint()
        item = self.scene().itemAt(pos.x(), pos.y(), QtGui.QTransform())
        if self.type == 'out' and item.type == 'in':
            self.new_line.source = self
            self.new_line.target = item
            # 既に接続済みのラインがあったら削除
            if len(item.parentItem().input_socket.in_lines) > 0:
                line = item.parentItem().input_socket.in_lines[0]
                line.target.in_lines.remove(line)
                line.source.out_lines.remove(line)
                item.parentItem().input_socket.in_lines = []
                self.scene().removeItem(line)

            item.parentItem().input_socket.in_lines.append(self.new_line)
            self.out_lines.append(self.new_line)
            self.new_line.point_b = item.get_center()
        elif self.type == 'in' and item.type == 'out':
            self.new_line.source = item
            self.new_line.target = self
            item.parentItem().output_socket.out_lines.append(self.new_line)
            self.in_lines.append(self.new_line)
            self.new_line.point_a = item.get_center()
        else:
            self.scene().removeItem(self.new_line)
            self.new_line = None
            super(NodeSocket, self).mouseReleaseEvent(event)

    def remove_old_in_line(self):
        # 既に接続済みのラインがあったら接続を解除。ラインは消さない
        if len(self.parentItem().input_socket.in_lines) > 0:
            line = self.parentItem().input_socket.in_lines[0]
            line.target.in_lines.remove(line)
            self.parentItem().input_socket.in_lines = []
            self.update()

    def delete_old_in_line(self):
        # 既に接続済みのラインがあったら存在ごと削除
        if len(self.parentItem().input_socket.in_lines) > 0:
            line = self.parentItem().input_socket.in_lines[0]
            line.target.in_lines.remove(line)
            line.source.out_lines.remove(line)
            self.parentItem().input_socket.in_lines = []
            self.scene().removeItem(line)
            self.update()

    def get_center(self):
        rect = self.boundingRect()
        center = QtCore.QPointF(rect.x() + rect.width() / 2, rect.y() + rect.height() / 2)
        center = self.mapToScene(center)
        return center


class NodeItem(QtWidgets.QGraphicsItem):
    def __init__(self):
        super(NodeItem, self).__init__()
        self.width = 100
        self.height = 60

        self.name = None
        self.rect = QtCore.QRect(0, 0, self.width, self.height)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.initUi()

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

        NodeLabel(QtCore.QRect(0, -20, 150, 20), self)

    def initUi(self):
        socket_size = 12
        socket_height = 15
        self.input_socket = NodeSocket(QtCore.QRect(0 - socket_size / 2, 25, 12, 12), self, 'in')
        self.output_socket = NodeSocket(QtCore.QRect(self.width - socket_size / 2, 25, 12, 12), self, 'out')

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
        super(NodeItem, self).mouseMoveEvent(event)
        for line in self.output_socket.out_lines:
            line.point_a = line.source.get_center()
            line.point_b = line.target.get_center()
        for line in self.input_socket.in_lines:
            line.point_a = line.source.get_center()
            line.point_b = line.target.get_center()

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu()
        make = menu.addAction('make')
        makeFromHere = menu.addAction('make from here')
        debugConnections = menu.addAction('debug connections')
        selectedAction = menu.exec_(event.screenPos())

        if selectedAction == debugConnections:
            print 'input_socket'
            for idx, line in enumerate(self.input_socket.in_lines):
                print '  Line {0}'.format(idx)
                print '    point_a: {0}'.format(line.point_a)
                print '    point_b: {0}'.format(line.point_b)
            print 'output_socket'
            for idx, line in enumerate(self.output_socket.out_lines):
                print '  Line {0}'.format(idx)
                print '    point_a: {0}'.format(line.point_a)
                print '    point_b: {0}'.format(line.point_b)


class NodeView(QtWidgets.QGraphicsView):
    """
    QGraphicsView for displaying the nodes.

    :param scene: QGraphicsScene.
    :param parent: QWidget.
    """

    def __init__(self, scene, parent):
        super(NodeView, self).__init__(parent)
        self.setObjectName('View')
        self.setScene(scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.SmartViewportUpdate)
        self.drag = False

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
            self.prevPos = event.pos()
            self.setCursor(QtCore.Qt.SizeAllCursor)
        elif event.button() == QtCore.Qt.LeftButton:
            self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        super(NodeView, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drag:
            delta = (self.mapToScene(event.pos()) - self.mapToScene(self.prevPos)) * -1.0
            center = QtCore.QPoint(self.viewport().width() / 2 + delta.x(), self.viewport().height() / 2 + delta.y())
            newCenter = self.mapToScene(center)
            self.centerOn(newCenter)
            self.prevPos = event.pos()
            return
        super(NodeView, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.drag:
            self.drag = False
            self.setCursor(QtCore.Qt.ArrowCursor)
        super(NodeView, self).mouseReleaseEvent(event)


'''
============================================================
---   UI CLASSES
============================================================
'''


class SideBar(QtWidgets.QFrame):
    def __init__(self, parent):
        super(SideBar, self).__init__(parent)
        self.setObjectName('SideBar')
        self.initUi()

    def initUi(self):
        # Frame.
        self.setFixedWidth(150)

        # Central Layout.
        self.CentralLayout = QtWidgets.QVBoxLayout(self)

        # Buttons.
        self.AddBoxButton = QtWidgets.QPushButton('Add Box')
        self.CentralLayout.addWidget(self.AddBoxButton)

        # Connections.
        self.initConnections()

    def initConnections(self):
        self.AddBoxButton.clicked.connect(self.clickedAddBoxButton)

    def clickedAddBoxButton(self):
        window = self.window()
        box = NodeItem()
        window.Scene.addItem(box)
        box.setPos(window.Scene.width() / 2, window.Scene.height() / 2)


class NodeWindow(QtWidgets.QMainWindow):
    def __init__(self, parent):
        super(NodeWindow, self).__init__(parent)
        self.setWindowTitle('Node Window')
        self.initUi()

    def initUi(self):
        # Window.
        self.setMinimumSize(400, 200)

        # Central Widget.
        self.CentralWidget = QtWidgets.QFrame()
        self.CentralWidget.setObjectName('CentralWidget')
        self.setCentralWidget(self.CentralWidget)

        # Central Layout.
        self.CentralLayout = QtWidgets.QHBoxLayout(self.CentralWidget)

        # GraphicsView.
        self.Scene = QtWidgets.QGraphicsScene()
        self.Scene.setObjectName('Scene')
        self.Scene.setSceneRect(0, 0, 32000, 32000)
        self.View = NodeView(self.Scene, self)
        self.CentralLayout.addWidget(self.View)

        # Side Bar.
        self.SideBar = SideBar(self)
        self.CentralLayout.addWidget(self.SideBar)

        # Color.
        self.initColor()

    def initColor(self):
        windowCss = '''
        QFrame {
            background-color: rgb(40,40,40);
            border: 1px solid rgb(90,70,30);
        }
        QFrame#SideBar {
            background-color: rgb(40,40,40);
            border: 1px solid rgb(255,255,255);
        }'''
        self.setStyleSheet(windowCss)


'''
============================================================
---   SHOW WINDOW
============================================================
'''


def mayaMainWindow():
    """
    Return the Maya main window widget as a Python object

    :return: Maya Main Window.
    """
    mainWindowPtr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(long(mainWindowPtr), QtWidgets.QWidget)


def main():
    mayaWindow = mayaMainWindow()
    nodeWindow = NodeWindow(mayaWindow)
    nodeWindow.show()


if __name__ == '__main__':
    main()

# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
