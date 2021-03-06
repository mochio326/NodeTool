# -*- coding: utf-8 -*-
from .vendor.Qt import QtCore, QtGui, QtWidgets
from shiboken2 import wrapInstance

from .view import View
from . import common


def aaa():
    print 'aaa'


class SideBar(QtWidgets.QFrame):
    def __init__(self, parent):
        super(SideBar, self).__init__(parent)
        self.setObjectName('SideBar')
        self.initUi()

    def initUi(self):
        # Frame.
        self.setFixedWidth(150)

        # Central Layout.
        self.central_layout = QtWidgets.QVBoxLayout(self)

        self.add_button('Add(＋)', 'Add')
        self.add_button('Subtract(ー)', 'Subtract')
        self.add_button('Multiply(×)', 'Multiply')
        self.add_button('Modulo(÷)', 'Modulo')
        self.add_button('1', '1')
        self.add_button('2', '2')
        self.add_button('3', '3')
        self.add_button('4', '4')

    def add_button(self, label, xml_name):
        self.add_box_button = QtWidgets.QPushButton(label)
        self.central_layout.addWidget(self.add_box_button)
        self.add_box_button.clicked.connect(lambda: self.clickedBoxButton(xml_name))

    def clickedBoxButton(self, xml_name):
        window = self.window()
        box = common.create_node_for_xml(xml_name, window.view)
        window.view.add_node_on_center(box)
        box.recalculation()

    def clickedAddPinButton(self):
        window = self.window()
        import node
        box = node.Node(name='test', label='label')
        p = box.add_port('in', QtCore.Qt.red, 'Int')
        p.expanded.connect(self.aaa)
        window.view.add_node_on_center(box)


class NodeWindow(QtWidgets.QMainWindow):
    def __init__(self, parent):
        super(NodeWindow, self).__init__(parent)
        self.setWindowTitle('Node Window')
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)

        self.initUi()
        self.move(200, 150)
        self.setFixedSize(900, 600)

    def initUi(self):
        # Window.
        self.setMinimumSize(500, 300)

        # Central Widget.
        self.central_widget = QtWidgets.QFrame()
        self.central_widget.setObjectName('CentralWidget')
        self.setCentralWidget(self.central_widget)

        # Central Layout.
        self.central_layout = QtWidgets.QHBoxLayout(self.central_widget)

        # GraphicsView.
        self.scene = QtWidgets.QGraphicsScene()
        self.scene.setObjectName('Scene')
        self.scene.setSceneRect(0, 0, 32000, 32000)
        self.view = View(self.scene, self)
        self.central_layout.addWidget(self.view)

        # Side Bar.
        self.side_bar = SideBar(self)
        self.central_layout.addWidget(self.side_bar)

        # Color.
        self.initColor()

    def initColor(self):
        window_css = '''
        QFrame {
            background-color: rgb(40,40,40);
            border: 1px solid rgb(90,70,30);
        }
        QFrame#SideBar {
            background-color: rgb(40,40,40);
            border: 1px solid rgb(255,255,255);
        }'''
        self.setStyleSheet(window_css)


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
    import maya.OpenMayaUI as OpenMayaUI
    mainWindowPtr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(long(mainWindowPtr), QtWidgets.QWidget)


def maya_main():
    mayaWindow = mayaMainWindow()
    nodeWindow = NodeWindow(mayaWindow)
    nodeWindow.show()

def main(parent=None):
    from sys import exit, argv
    app = QtWidgets.QApplication(argv)
    nodeWindow = NodeWindow(parent)
    nodeWindow.show()
    exit(app.exec_())

if __name__ == '__main__':
    main()

# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
