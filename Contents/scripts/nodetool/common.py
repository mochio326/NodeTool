# -*- coding: utf-8 -*-
from .vendor.Qt import QtCore, QtGui, QtWidgets
from . import node
from . import port
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
    p = tree.findall('Port')
    create_ports_for_xml(p, n)
    return n


def create_ports_for_xml(ports_xml, parent):
    port_color = PortColor()
    for _p in ports_xml:
        if isinstance(parent, node.Node):
            pp = parent.add_port(label=_p.attrib.get('Label'), port_type=_p.attrib.get('Type'),
                                 color=getattr(port_color, _p.attrib.get('ValueType')),
                                 value_type=_p.attrib.get('ValueType'))

        else:

            pp = port.Port(parent=parent, label=_p.attrib.get('Label'), port_type=_p.attrib.get('Type'),
                           color=getattr(port_color, _p.attrib.get('ValueType')), value_type=_p.attrib.get('ValueType'))
        _p_find = _p.findall('Port')
        print _p_find
        create_ports_for_xml(_p_find, pp)

# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
