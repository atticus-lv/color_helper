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

    def create_node_group(self, palette, create):
        if palette.node_group is not None:
            nt = palette.node_group
            for node in nt.nodes:
                nt.nodes.remove(node)
            #上面虽然删除了节点组里所有节点，包括组输出节点，但节点组的输出端口还是在的，用下面的方法删除输出端
            for item in nt.interface.items_tree:
                if item.item_type == 'SOCKET':
                    if item.in_out == 'OUTPUT'or item.in_out == 'INPUT':
                        nt.interface.remove(item)

        else:
            nt = bpy.data.node_groups.new(palette.name, 'ShaderNodeTree')
            palette.node_group = nt

        loc_x, loc_y = 0, 0
        node_output = nt.nodes.new('NodeGroupOutput')
        node_output.location = len(palette.colors) * 150 + 200, 0
        node_input = nt.nodes.new('NodeGroupInput')
        node_input.location = (len(palette.colors) - 2) * 150, -(len(palette.colors) + 3) * 50

        for i, color in enumerate(palette.colors):
            color = color.color
            colornode = nt.nodes.new('ShaderNodeRGB')
            colornode.outputs[0].default_value = color
            colornode.location = loc_x + i * 150, loc_y - i * 50

            #添加颜色输出端口，端口名加上序号，方便知道那个端口是色板里第几个颜色
            if bpy.app.version >= (4, 0, 0):
                nt.interface.new_socket(name="Color"+"  _"+str(i+1), in_out='OUTPUT',socket_type='NodeSocketColor')

            nt.links.new(colornode.outputs[0], node_output.inputs[i])

        node_ramp = nt.nodes.new(type="ShaderNodeValToRGB")
        node_ramp.location = node_input.location[0] + 200, node_input.location[1]
        node_ramp.color_ramp.elements.remove(node_ramp.color_ramp.elements[0])
        node_ramp.color_ramp.elements[0].position = 0
        for i, color_item in enumerate(palette.colors):
            if i > 0:
                node_ramp.color_ramp.elements.new(position=1 / (len(palette.colors) - 1) * i)
            node_ramp.color_ramp.elements[i].color = color_item.color

        #改为4.0的新增渐变的端口
        if bpy.app.version >= (4, 0, 0):
            nt.interface.new_socket(name="Ramp Fac", in_out='INPUT',socket_type='NodeSocketFloat')
            nt.interface.new_socket(name="Ramp", in_out='OUTPUT',socket_type='NodeSocketColor')

        nt.links.new(node_input.outputs[0], node_ramp.inputs[0])
        nt.links.new(node_ramp.outputs[0], node_output.inputs["Ramp"])

        if not create: return
        # 检查当前操作空间是否是在材质节点编辑器里
        if bpy.context.area.type != 'NODE_EDITOR' or bpy.context.space_data.tree_type != 'ShaderNodeTree':
            self.report({'WARNING'}, "在节点编辑器里按Shift后才会自动添加节点组！")
            return

        loc_x, loc_y = bpy.context.space_data.cursor_location
        bpy.ops.node.select_all(action='DESELECT')
        edit_tree = bpy.context.space_data.edit_tree

        if edit_tree != nt and not (edit_tree.nodes.active and
                                    hasattr(edit_tree.nodes.active, 'node_tree') and
                                    getattr(edit_tree.nodes.active, 'node_tree') == nt):
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
