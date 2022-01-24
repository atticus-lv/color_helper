import bpy
import os
from bpy.props import EnumProperty, IntProperty, BoolProperty


class CH_OT_create_nodes_from_palette(bpy.types.Operator):
    """Create/Update shader node group from this palette\nShift to create/update and add group node to current material"""
    bl_idname = 'ch.create_nodes_from_palette'
    bl_label = 'Create Color From Palette'

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
        self.create_node_group(palette, create=event.shift)
        return {'FINISHED'}

    def create_node_group(self, palette, create):
        if palette.node_group is not None:
            nt = palette.node_group
            for node in nt.nodes:
                nt.nodes.remove(node)
        else:
            nt = bpy.data.node_groups.new(palette.name, 'ShaderNodeTree')
            palette.node_group = nt

        loc_x, loc_y = 0, 0

        node_output = nt.nodes.new('NodeGroupOutput')

        for i, color_item in enumerate(palette.colors):
            color = color_item.color
            node = nt.nodes.new('ShaderNodeRGB')
            node.outputs[0].default_value = color
            node.location = loc_x + i * 150, loc_y - i * 50
            nt.links.new(node.outputs[0], node_output.inputs[i])

        node_output.location = len(palette.colors) * 150 + 200, 0

        # # Create Node Group
        if bpy.context.area.ui_type != 'NODE_EDITOR': return
        if bpy.context.space_data.edit_tree is None or not create: return

        loc_x, loc_y = bpy.context.space_data.cursor_location
        bpy.ops.node.select_all(action='DESELECT')

        edit_tree = bpy.context.space_data.edit_tree

        if edit_tree != nt and not (edit_tree.nodes.active and
                                    hasattr(edit_tree.nodes.active, 'node_tree') and
                                    getattr(edit_tree.nodes.active, 'node_tree') == nt):
            group_node = edit_tree.nodes.new('ShaderNodeGroup')
            group_node.node_tree = nt
            group_node.location = loc_x, loc_y

            bpy.ops.transform.translate('INVOKE_DEFAULT')


def draw_context(self, context):
    layout = self.layout
    layout.operator('ch.create_nodes_from_palette', text='Get Image Color')
    layout.separator()


def register():
    bpy.utils.register_class(CH_OT_create_nodes_from_palette)
    # bpy.types.NODE_MT_context_menu.prepend(draw_context)


def unregister():
    bpy.utils.unregister_class(CH_OT_create_nodes_from_palette)
    # bpy.types.NODE_MT_context_menu.remove(draw_context)
