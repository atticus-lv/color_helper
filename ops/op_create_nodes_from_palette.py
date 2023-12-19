import bpy
import os
from bpy.props import EnumProperty, IntProperty, BoolProperty


class CH_OT_create_nodes_from_palette(bpy.types.Operator):
    """Create/Update shader node group from this palette\nShift to add group node to current material\nCtrl to toggle auto update"""
    bl_idname = 'ch.create_nodes_from_palette'
    bl_label = 'Create Node Group From Palette'

    palette_index: IntProperty()

    @classmethod
    def poll(cls, context):
        return (
                (context.area.ui_type == 'VIEW_3D') or
                (hasattr(context.space_data, 'edit_tree') and
                 context.space_data.edit_tree and
                 context.space_data.edit_tree.bl_idname == 'ShaderNodeTree')
        )

    def _return(self, error_msg=None, info_msg=None):
        if error_msg:
            self.report({'ERROR'}, error_msg)
        elif info_msg:
            self.report({'INFO'}, info_msg)

        return {'FINISHED'}

    def invoke(self, context, event):
        collection = context.scene.ch_palette_collection[context.scene.ch_palette_collection_index]
        palette = collection.palettes[self.palette_index]
        if event.ctrl:
            palette.node_group_update = False if palette.node_group_update == True else True
            context.area.tag_redraw()
        self.create_node_group(palette, create=event.shift)
        return {'FINISHED'}

    def ensure_palette_node_group(self, palette):
        if palette.node_group is not None:
            nt = palette.node_group
            for node in nt.nodes:
                nt.nodes.remove(node)
        else:
            nt = bpy.data.node_groups.new(palette.name, 'ShaderNodeTree')
            palette.node_group = nt

        return nt

    def create_node_group(self, palette, create):
        from ..utils.nt_helper import CH_NodeTreeHelper as CH

        NAME_RAMP_FAC = 'Ramp Fac'
        NAME_RAMP = 'Ramp'
        SEP_X = 150
        SEP_Y = 50

        nt = self.ensure_palette_node_group(palette)
        colors = [item.color for item in palette.colors]
        # convert old version
        self.convert_old_interface_items(nt, len(colors))
        # make nodes
        rgb_nodes = CH.rgb_nodes_from_colors(nt, colors)
        node_input, node_output = CH.ensure_node_group_inout(nt)
        node_ramp = CH.ramp_node_from_colors(nt, colors)
        # set location for better view
        CH.offset_nodes(rgb_nodes, offset=(SEP_X, SEP_Y))
        node_output.location = len(palette.colors) * SEP_X + SEP_X, 0
        node_input.location = (len(palette.colors) - 2) * SEP_X, -(len(palette.colors) + 3) * SEP_Y
        node_ramp.location = node_input.location[0] + SEP_X, node_input.location[1]
        # interface items / links
        for i, rgb_node in enumerate(rgb_nodes):
            name = f'Color_{i + 1}'
            CH.ensure_interface_item(nt, name, 'OUTPUT', 'NodeSocketColor')

            nt.links.new(rgb_node.outputs[0], node_output.inputs[name])

        ramp_item = CH.ensure_interface_item(nt, NAME_RAMP, 'OUTPUT', 'NodeSocketColor')
        nt.interface.move(ramp_item, -1)  # move to top

        CH.ensure_interface_item(nt, NAME_RAMP_FAC, 'INPUT', 'NodeSocketFloat')

        nt.links.new(node_ramp.outputs[0], node_output.inputs[NAME_RAMP])
        nt.links.new(node_input.outputs[0], node_ramp.inputs[0])

        if not create: return
        # 检查当前操作空间是否是在材质节点编辑器里
        self.move_nodes(nt)

    def convert_old_interface_items(self, nt, length):
        """Convert the old version color node group to prevent cut links"""
        import re
        from ..utils.nt_helper import CH_NodeTreeHelper as CH

        l = []
        for item in CH._iter_node_interface(nt, type='OUTPUT'):
            if item.name == 'Color' and item.socket_type == 'NodeSocketColor' and item.in_out == 'OUTPUT':
                l.append(item)

        if len(l) == length:
            for i, item in enumerate(l):
                item.name = f'Color_{i + 1}'

    def move_nodes(self, nt):
        if bpy.context.area.type != 'NODE_EDITOR' or bpy.context.space_data.tree_type != 'ShaderNodeTree':
            self.report({'WARNING'}, "在节点编辑器里按Shift后才会自动添加节点组！")
            return

        loc_x, loc_y = bpy.context.space_data.cursor_location
        bpy.ops.node.select_all(action='DESELECT')
        edit_tree = bpy.context.space_data.edit_tree

        if edit_tree is not nt and not (
                edit_tree.nodes.active and
                hasattr(edit_tree.nodes.active, 'node_tree') and
                getattr(edit_tree.nodes.active, 'node_tree') is nt):
            group_node = edit_tree.nodes.new('ShaderNodeGroup')
            group_node.node_tree = nt

            group_node.location = loc_x - bpy.context.region.width, loc_y

            bpy.ops.transform.translate('INVOKE_DEFAULT')


class CH_OT_create_ramp_from_palette(bpy.types.Operator):
    bl_idname = 'ch.create_ramp_from_palette'
    bl_label = 'Create Ramp Node'

    palette_index: IntProperty()

    @classmethod
    def poll(cls, context):
        return (hasattr(context.space_data, 'edit_tree') and
                context.space_data.edit_tree and
                context.space_data.edit_tree.bl_idname == 'ShaderNodeTree')

    def execute(self, context):
        collection = context.scene.ch_palette_collection[context.scene.ch_palette_collection_index]
        palette = collection.palettes[self.palette_index]

        loc_x, loc_y = context.space_data.cursor_location

        if len(palette.colors) == 0: return {'CANCELLED'}

        nt = bpy.context.space_data.edit_tree

        bpy.ops.node.select_all(action='DESELECT')

        node_ramp = nt.nodes.new(type="ShaderNodeValToRGB")
        node_ramp.location = loc_x - context.region.width, loc_y
        node_ramp.color_ramp.elements.remove(node_ramp.color_ramp.elements[0])
        node_ramp.color_ramp.elements[0].position = 0

        for i, color in enumerate(palette.colors):
            if i > 0:
                node_ramp.color_ramp.elements.new(position=1 / (len(palette.colors) - 1) * i)
            node_ramp.color_ramp.elements[i].color = color.color

        bpy.ops.transform.translate('INVOKE_DEFAULT')

        return {'FINISHED'}


def draw_context(self, context):
    layout = self.layout
    layout.operator('ch.create_nodes_from_palette', text='Get Image Color')
    layout.separator()


def register():
    bpy.utils.register_class(CH_OT_create_nodes_from_palette)
    bpy.utils.register_class(CH_OT_create_ramp_from_palette)
    # bpy.types.NODE_MT_context_menu.prepend(draw_context)


def unregister():
    bpy.utils.unregister_class(CH_OT_create_nodes_from_palette)
    bpy.utils.unregister_class(CH_OT_create_ramp_from_palette)
    # bpy.types.NODE_MT_context_menu.remove(draw_context)
