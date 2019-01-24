# -*- coding: utf-8 -*-
from .vendor.Qt import QtCore, QtGui, QtWidgets
from . import node
from . import port


class Pin(node.Node):
    TYPE = 'Pin'

    def __init__(self, *args, **kwargs):
        self.init_color = QtCore.Qt.gray
        self.init_type = None
        super(Pin, self).__init__(*args, **kwargs)
        self.input_port = port.Port(self, 'in', self.init_color, self.init_type, self.port_init_y)
        self.output_port = port.Port(self, 'out', self.init_color, self.init_type, self.port_init_y)
        self.ports.append(self.input_port)
        self.ports.append(self.output_port)

    def return_initial_state(self):
        # 接続が無くなったら初期状態の見た目に戻す
        if len(self.input_port.lines) == 0 and len(self.output_port.lines) == 0:
            self.input_port.value_type = self.init_type
            self.input_port.color = self.init_color
            self.input_port.hoverLeaveEvent(None)
            self.output_port.value_type = self.init_type
            self.output_port.color = self.init_color
            self.output_port.hoverLeaveEvent(None)

    def propagate(self, source, target, line):
        # 片方のソケットに接続された際に値のタイプや色を伝搬させる
        if target == self.input_port:
            pair_port = self.output_port
        else:
            pair_port = self.input_port

        if len(pair_port.lines) == 0:
            # 反対側のソケットの処理
            pair_port.value_type = source.value_type
            pair_port.color = source.color
            pair_port.hoverLeaveEvent(None)
            # 自分自身のソケットの処理
            target.value_type = source.value_type
            target.color = source.color
            target.hoverLeaveEvent(None)
            # ラインも色変え等
            line.color = source.color
            line.hoverLeaveEvent(None)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
