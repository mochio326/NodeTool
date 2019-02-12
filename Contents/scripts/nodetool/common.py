# -*- coding: utf-8 -*-
from .vendor.Qt import QtCore, QtGui, QtWidgets
from . import node
import xml.etree.ElementTree as ET
import glob
import os

class PortColor(object):
    Int = QtCore.Qt.red
    Bool = QtCore.Qt.green

    def __setattr__(self, *_):
        pass


def get_node_file_list():
    path = get_xml_dir()
    for f in glob.glob(r'{}\*.xml'.format(path)):
        yield f


def get_xml_dir():
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.normpath(os.path.join(base, 'node_db'))
    return path


def create_node_for_xml(xml_file=''):
    _dir = get_xml_dir()
    tree = ET.parse('{}\{}.xml'.format(_dir, xml_file))
    n = node.Node(name=xml_file, label=tree._root.attrib['Label'])
    _ports = tree.findall('Port')
    port_color = PortColor()
    for _p in _ports:
        p = n.add_port(_p.attrib['Type'], getattr(port_color, _p.attrib['ValueType']), _p.attrib['ValueType'],
                   _p.attrib['Label'])

    return n

# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
