# # -*- coding: utf-8 -*-
from mochinode.vendor.Qt import QtCore, QtGui, QtWidgets
from mochinode import Node, View, Port
from shiboken2 import wrapInstance
import uuid

from . import node
from . import common

class View2(View):
    def __init__(self, *args, **kwargs):
        super(View2, self).__init__(*args, **kwargs)

    def mouseReleaseEvent(self, event):
        super(View2, self).mouseReleaseEvent(event)

        if event.button() == QtCore.Qt.RightButton:
            menu = QtWidgets.QMenu()
            save = menu.addAction('save')
            load = menu.addAction('load')
            selected_action = menu.exec_(event.globalPos())

            if selected_action == save:
                common.scene_save(self)
            if selected_action == load:
                common.scene_load(self)

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

        # 貼り付け前に保存データ内のノードIDを変更することでIDの重複を避ける
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

    def _cut(self):
        pass

    def _undo(self):
        pass

    def _redo(self):
        pass


class Window(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)

        self.setWindowTitle('mochinode test app2')

        self.resize(800, 600)
        hbox = QtWidgets.QHBoxLayout()
        hbox.setSpacing(2)
        hbox.setContentsMargins(2, 2, 2, 2)
        self.setLayout(hbox)

        scene = QtWidgets.QGraphicsScene()
        scene.setObjectName('Scene')
        scene.setSceneRect(0, 0, 32000, 32000)
        self.view = View2(scene, self)

        self.central_layout = QtWidgets.QVBoxLayout()
        hbox.addWidget(self.view)
        hbox.addLayout(self.central_layout, 10)

        run_button = QtWidgets.QPushButton('Run !!!')
        run_button.clicked.connect(lambda: common.nodes_recalculation(self.view))
        run_button.setStyleSheet("background-color: rgb(244, 72, 66);")
        self.central_layout.addWidget(self.add_box_button)

        layoutBtn = QtWidgets.QPushButton('Auto Layout')
        layoutBtn.clicked.connect(lambda: self.view.auto_layout())
        layoutBtn.setStyleSheet("background-color: rgb(244, 238, 65);")
        # vbox.addWidget(self.nameFld)
        # vbox.addWidget(addBtn)
        self.central_layout.addWidget(layoutBtn)

        self.add_button('Add(＋)', 'Add')
        self.add_button('Subtract(ー)', 'Subtract')
        self.add_button('Multiply(×)', 'Multiply')
        self.add_button('Modulo(÷)', 'Modulo')
        self.add_button('1', '1')
        self.add_button('2', '2')
        self.add_button('3', '3')
        self.add_button('4', '4')



        self.central_layout.addStretch(1)



    def add_button(self, label, xml_name):
        self.add_box_button = QtWidgets.QPushButton(label)
        self.central_layout.addWidget(self.add_box_button)
        self.add_box_button.clicked.connect(lambda: self.clickedBoxButton(xml_name))

    def clickedBoxButton(self, xml_name):
        box = node.create_node_for_xml(xml_name, self.view)
        self.view.add_node_on_center(box)
        # box.recalculation()


'''
============================================================
---   SHOW WINDOW
============================================================
'''


def main(parent=None):
    from sys import exit, argv
    app = QtWidgets.QApplication(argv)
    nodeWindow = Window(parent)
    nodeWindow.show()
    exit(app.exec_())


def maya_main():
    import maya.OpenMayaUI as OpenMayaUI
    mainWindowPtr = OpenMayaUI.MQtUtil.mainWindow()
    mayaWindow = wrapInstance(long(mainWindowPtr), QtWidgets.QWidget)
    nodeWindow = Window()
    nodeWindow.show()


if __name__ == '__main__':
    main()
