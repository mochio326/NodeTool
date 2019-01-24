# -*- coding: utf-8 -*-
from .vendor.Qt import QtCore, QtGui, QtWidgets
from . import node
import xml.etree.ElementTree as ET


def create_node_for_xml(xml_file=''):
    tree = ET.parse(
        r'C:\Program Files\Autodesk\ApplicationPlugins\NodeTool\Contents\scripts\nodetool\node_db\hogera.xml')
    n = node.Node(label=tree._root.attrib['label'])
    pins = tree.findall('Pin')
    for pin in pins:
        n.add_port(pin.attrib['type'], QtCore.Qt.green, pin.attrib['value_type'], pin.attrib['label'])
    return n

# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
