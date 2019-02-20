# -*- coding: utf-8 -*-
from .vendor.Qt import QtCore, QtGui, QtWidgets
from . import node
from . import port
from . import line
import xml.etree.ElementTree as ET
import glob
import os
import json

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
    n.deploying_port()
    return n


def create_node_for_save_data(scene, save_data):
    node = create_node_for_xml(save_data['name'])
    scene.add_item(node)
    load_node_data(node, save_data, False)


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
        create_ports_for_xml(_p_find, pp)

def load_node_data(node, save_data, ports_only=False):
    for _p in node.children_ports_all_iter():
        _p.children_port_expand = save_data['ports'][_p.name]
    node.deploying_port()
    if ports_only:
        return
    node.id = save_data['id']
    node.setZValue(save_data['z_value'])
    node.setX(save_data['x'])
    node.setY(save_data['y'])


def scene_save(view):
    save_data = {}
    nodes = []
    for _n in node.Node.scene_nodes_iter(view):
        nodes.append(_n.save_data)
    save_data['node'] = nodes

    lines = []
    for _l in line.Line.scene_lines_iter(view):
        lines.append(_l.save_data)
    save_data['line'] = lines

    not_escape_json_dump(r'c:\temp\node_tool.json', save_data)


def scene_load(view):
    data = not_escape_json_load(r'c:\temp\node_tool.json')
    view.clear()

    nodes = []
    for _n in data['node']:
        node = create_node_for_xml(_n['name'])
        view.add_item_on_center(node)
        load_node_data(node, _n, False)
        nodes.append(node)

    for _l in data['line']:
        line_connect_for_save_data(_l, view)

    for _n in nodes:
        for _p in _n.children_ports_all_iter():
            _p.create_temp_line()


def line_connect_for_save_data(line_data, view):
    new_line = line.Line(QtCore.QPointF(0,0), QtCore.QPointF(0,0), None)
    for _n in node.Node.scene_nodes_iter(view):
        if line_data['sauce']['node_id'] == _n.id:
            sauce = _n.port[line_data['sauce']['port_name']]
        if line_data['target']['node_id'] == _n.id:
            target = _n.port[line_data['target']['port_name']]
    sauce.connect(new_line)
    target.connect(new_line)
    new_line.color = target.color
    view.add_item(new_line)

def not_escape_json_dump(path, data):
    # http://qiita.com/tadokoro/items/131268c9a0fd1cf85bf4
    # 日本語をエスケープさせずにjsonを読み書きする
    text = json.dumps(data, sort_keys=True, ensure_ascii=False, indent=2)
    with open(path, 'w') as fh:
        fh.write(text.encode('utf-8'))


def not_escape_json_load(path):
    if os.path.isfile(path) is False:
        return None
    with open(path) as fh:
        data = json.loads(fh.read(), "utf-8")
    return data



# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
