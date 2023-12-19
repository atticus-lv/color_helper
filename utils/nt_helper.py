import bpy
from dataclasses import dataclass
from mathutils import Color


@dataclass
class NodeTreeHelper():
    nt: bpy.types.NodeTree = None

    @staticmethod
    def _is_item_socket(item: bpy.types.NodeTreeInterfaceItem) -> bool:
        """since blender 4.0.0, socket is a item of node tree, else panel"""
        return item.item_type == 'SOCKET'

    @staticmethod
    def _is_input_node(node: bpy.types.Node) -> bool:
        return node.bl_idname == 'NodeGroupInput'

    @staticmethod
    def _is_output_node(node: bpy.types.Node) -> bool:
        return node.bl_idname == 'NodeGroupOutput'

    @staticmethod
    def is_ng_input_output(node: bpy.types.Node) -> bool:
        return NodeTreeHelper._is_input_node(node) or NodeTreeHelper._is_output_node(node)

    @staticmethod
    def _true_socket_type(socket: bpy.types.NodeSocket | bpy.types.NodeTreeInterfaceSocket) -> str:
        """remove socket subtype, subtype can not be add to interface directly"""

        if hasattr(socket, 'bl_subtype_label'):
            return socket.bl_idname.replace(socket.bl_subtype_label, '')
        return socket.bl_idname

    @staticmethod
    def make_node(nt: bpy.types.NodeTree, node_idname: str, location: tuple = (0, 0)) -> bpy.types.NodeTree:
        """easy make node with init location"""
        node = nt.nodes.new(node_idname)
        node.location = location
        return node

    @staticmethod
    def make_links(nt: bpy.types.NodeTree, socket_from: bpy.types.NodeSocket, socket_to: bpy.types.NodeSocket):
        """
        make links between two sockets
        sine blender 4.0.0, socket is a item of node tree
        so new to create new interface socket when link between input pr output node
        """

        node_from = socket_from.node
        node_to = socket_to.node

        if NodeTreeHelper.is_ng_input_output(node_from):
            new_socket_from_item = nt.interface.new_socket(name=socket_to.name, in_out='INPUT',
                                                           socket_type=NodeTreeHelper._true_socket_type(socket_to))
        if NodeTreeHelper.is_ng_input_output(node_to):
            new_socket_to_item = nt.interface.new_socket(name=socket_from.name, in_out='OUTPUT',
                                                         socket_type=NodeTreeHelper._true_socket_type(socket_from))

        return nt.links.new(socket_from, socket_to)

    # interface item
    @staticmethod
    def _make_nt_interface_item(nt: bpy.types.NodeTree, name: str, in_out: str, socket_type: str):
        """make socket for node tree interface"""
        socket = nt.interface.new_socket(name=name, in_out=in_out, socket_type=socket_type)
        return socket

    @staticmethod
    def _iter_node_interface(nt: bpy.types.NodeTree,
                             type: str = 'INPUT') -> bpy.types.NodeTreeInterfaceSocket:
        for item in nt.interface.items_tree:
            if NodeTreeHelper._is_item_socket(item) and item.in_out == type:
                yield item

    @staticmethod
    def ensure_interface_item(nt: bpy.types.NodeTree, name: str, in_out: str, socket_type: str):
        item = None
        for _item in NodeTreeHelper._iter_node_interface(nt, in_out):
            if _item.name == name and _item.socket_type == socket_type:
                item = _item
                break

        if not item:
            item = NodeTreeHelper._make_nt_interface_item(nt, name, in_out, socket_type)

        return item

    @staticmethod
    def ensure_node_group_inout(nt: bpy.types.NodeTree) -> tuple[bpy.types.Node, bpy.types.Node]:
        """find socket by interface item"""
        node_input = node_output = None
        for node in nt.nodes:
            if NodeTreeHelper._is_input_node(node):
                node_input = node
            elif NodeTreeHelper._is_output_node(node):
                node_output = node

        if node_input is None:
            node_input = NodeTreeHelper.make_node(nt, 'NodeGroupInput')
        if node_output is None:
            node_output = NodeTreeHelper.make_node(nt, 'NodeGroupOutput')

        return node_input, node_output

    # TODO cleanup method
    @staticmethod
    def find_links(nt: bpy.types.NodeTree, in_out: str):
        node_name = 'NodeGroupInput' if type == 'INPUT' else 'NodeGroupOutput'
        pass

    @staticmethod
    def clean_node_interface(nt: bpy.types.NodeTree):
        """clean node interface sockets"""
        for item in nt.interface.items_tree:
            if not NodeTreeHelper._is_item_socket(item): continue
            if item.in_out not in {'INPUT', 'OUTPUT'}: continue

            nt.interface.remove(item)


class CH_NodeTreeHelper(NodeTreeHelper):

    @staticmethod
    def rgb_nodes_from_colors(nt: bpy.types.NodeTree, colors: list[Color]) -> list[bpy.types.Node]:
        """create rgb nodes from colors"""
        rgbNodes = []
        for i, color in enumerate(colors):
            rgbNode = CH_NodeTreeHelper.make_node(nt, 'ShaderNodeRGB')
            rgbNode.outputs[0].default_value = color
            rgbNodes.append(rgbNode)

        return rgbNodes

    @staticmethod
    def ramp_node_from_colors(nt: bpy.types.NodeTree, colors: list[Color]) -> bpy.types.Node:
        node_ramp = CH_NodeTreeHelper.make_node(nt, 'ShaderNodeValToRGB')
        node_ramp.color_ramp.elements.remove(node_ramp.color_ramp.elements[0])
        node_ramp.color_ramp.elements[0].position = 0
        for i, color in enumerate(colors):
            if i > 0:
                node_ramp.color_ramp.elements.new(position=1 / (len(colors) - 1) * i)
            node_ramp.color_ramp.elements[i].color = color

        return node_ramp

    @staticmethod
    def offset_nodes(nodes: list[bpy.types.Node], offset: tuple[int, int] = (150, 50)):
        """offset nodes location, for better view"""
        start_x, start_y = nodes[0].location.x, nodes[0].location.y
        for i, node in enumerate(nodes):
            node.location.x += start_x + offset[0] * i
            node.location.y += start_y + offset[1] * i
