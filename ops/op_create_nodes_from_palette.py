import bpy
import os
from bpy.props import EnumProperty, IntProperty, BoolProperty


class CH_OT_create_nodes_from_palette(bpy.types.Operator):
    """从此调色板创建/更新着色器节点组\nShift将组节点添加到当前材质\nCtrl切换为自动更新"""
    #"""Create/Update shader node group from this palette\nShift to add group node to current material\nCtrl to toggle auto update"""
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
        #     """
        # 从调色板创建节点组，用于创建和编辑着色节点。
        # :param palette: 调色板对象，包含颜色信息和节点组等。
        # :param create: 是否创建节点组。
        # """
        # 如果调色板已经有关联的节点组，删除其中的所有节点
        if palette.node_group is not None:
            nt = palette.node_group
            for node in nt.nodes:
                nt.nodes.remove(node)
        else:  
            nt = bpy.data.node_groups.new(palette.name, 'ShaderNodeTree')
            palette.node_group = nt

        loc_x, loc_y = 0, 0
        # 创建节点组的输出节点
        node_output = nt.nodes.new('NodeGroupOutput')
        node_output.location = len(palette.colors) * 150 + 200, 0
        # 创建节点组的输入节点
        node_input = nt.nodes.new('NodeGroupInput')
        node_input.location = (len(palette.colors) - 2) * 150, -(len(palette.colors) + 3) * 50

        # ramp node# 创建渐变节点，将渐变输出端口放到第一了，为的是如果渐变端口有连接，当颜色数量增加后，
        #更新节点组后如果最后一个是渐变端口原本的连接就会断开，所以移到第一个
        node_ramp = nt.nodes.new(type="ShaderNodeValToRGB")
        node_ramp.location = node_input.location[0] + 200, node_input.location[1]
        node_ramp.color_ramp.elements.remove(node_ramp.color_ramp.elements[0])
        node_ramp.color_ramp.elements[0].position = 0
        # 为每个颜色创建色调映射点，并将它们连接到输出节点
        for i, color_item in enumerate(palette.colors):
            if i > 0:
                node_ramp.color_ramp.elements.new(position=1 / (len(palette.colors) - 1) * i)
            node_ramp.color_ramp.elements[i].color = color_item.color

        if bpy.app.version >= (4, 0, 0):
            nt.interface.new_socket(name="Ramp Fac", in_out='INPUT',socket_type='NodeSocketFloat')
            nt.interface.new_socket(name="Ramp", in_out='OUTPUT',socket_type='NodeSocketColor')

        nt.links.new(node_input.outputs[0], node_ramp.inputs[0])
        nt.links.new(node_ramp.outputs[0], node_output.inputs[0])#-1#len(palette.colors)

        # RGB nodes# 创建RGB节点来表示每个颜色，并将其连接到输出节点
        for i, color in enumerate(palette.colors):
            color = color.color
            colornode = nt.nodes.new('ShaderNodeRGB')
            colornode.outputs[0].default_value = color
            colornode.location = loc_x + i * 150, loc_y - i * 50

            # if bpy.app.version >= (3, 5, 0):
            #     nt.outputs.new('NodeSocketColor', 'Color')
            if bpy.app.version >= (4, 0, 0):
                nt.interface.new_socket(name="Color"+"  _"+str(i+1), in_out='OUTPUT',socket_type='NodeSocketColor')

            nt.links.new(colornode.outputs[0], node_output.inputs[i+1])

        # 重新修输出端口名称,第一次生成节点组时端口名都是对的，但当颜色数量变化后会渐变端口的名字序号就不对了
        counter = 0
        for item in nt.interface.items_tree:
            if item.item_type == 'SOCKET':
                if item.in_out == 'OUTPUT':
                    item.name = f'Color_{counter}'
                    counter += 1
                    if item.index == 0:#len(palette.colors):
                        item.name = 'Ramp'#设置第1个名为渐变

        #把上面该连接的都搞定后再删除多的端口，如果最开始删除全部端口，会把节点组之前的外面连接到其它材质节点的连接都清空！！！
        nt = palette.node_group
        for item in nt.interface.items_tree:
            if item.item_type == 'SOCKET':
                if item.in_out == 'OUTPUT' and item.index > len(palette.colors):
                    nt.interface.remove(item)
                if item.in_out == 'INPUT' and item.index > len(palette.colors)+1:
                    nt.interface.remove(item)
       
        # 如果需要创建节点组，将其在编辑树中创建Create Node Group
        if not create: return
        # 检查当前操作空间是否是在材质节点编辑器里
        if bpy.context.area.type != 'NODE_EDITOR' or bpy.context.space_data.tree_type != 'ShaderNodeTree':
            self.report({'WARNING'}, "在节点编辑器里按Shift后才会自动添加节点组！")
            return
        # 获取光标位置，创建组节点并将节点组链接到编辑树
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
