import bpy
from bpy.props import *


def get_coll_active():
    collection = bpy.context.scene.ch_palette_collection[bpy.context.scene.ch_palette_collection_index]

    return collection


class CH_OT_select_collection(bpy.types.Operator):
    bl_idname = "ch.select_collection"
    bl_label = 'Select'
    bl_options = {'INTERNAL', 'UNDO'}

    index: IntProperty()

    def execute(self, context):
        context.scene.ch_palette_collection_index = self.index
        return {'FINISHED'}


class CH_MT_collection_switcher(bpy.types.Menu):
    bl_label = "Selection Collection"
    bl_idname = "CH_MT_collection_switcher"

    @classmethod
    def poll(cls, context):
        return len(context.scene.ch_palette_collection) > 0

    def draw(self, context):
        layout = self.layout

        for i, item in enumerate(context.scene.ch_palette_collection):
            row = layout.row()

            row.operator("ch.select_collection", text=item.name).index = i

        layout.separator()
        layout.label(text='Select Collection')


class CH_PT_collection_manager(bpy.types.Panel):
    bl_label = "Collection Manager"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'

    def draw(self, context):
        layout = self.layout

        for i, item in enumerate(context.scene.ch_palette_collection):
            row = layout.box().row()
            d = row.row()
            d.alert = True
            d.operator('ch.remove_collection', icon='X', text=''
                       ).collection_index = i
            row.prop(item, 'name', text='')

        layout.box().operator('ch.add_collection', icon='ADD', text='New Collection', emboss=False)


class CH_OT_palette_extra_op_caller(bpy.types.Operator):
    bl_label = "Extra"
    bl_idname = 'ch.palette_extra_op_caller'

    collection_index: IntProperty()
    palette_index: IntProperty()

    @classmethod
    def poll(self, context):
        return len(context.scene.ch_palette_collection) != 0

    def invoke(self, context, event):
        coll = get_coll_active()
        index = self.palette_index
        title = f'{coll.palettes[index].name}'

        def draw_custom_menu(self, context):
            layout = self.layout
            layout.operator_context = "INVOKE_DEFAULT"

            layout.operator('ch.create_ramp_from_palette', icon='COLORSET_08_VEC').palette_index = index
            layout.separator()

            layout.operator('ch.copy_palette', icon='DUPLICATE')
            layout.operator('ch.move_palette', icon='FORWARD').palette_index = index
            layout.separator()

            layout.operator('ch.export_palette',
                            text='Make Palette Image',
                            icon='COLORSET_13_VEC'
                            ).palette_index = index

            layout.separator()
            layout.operator('ch.remove_palette', text='Remove', icon='X').palette_index = index

        context.window_manager.popup_menu(draw_custom_menu, title=title)

        return {"FINISHED"}


class SidePanelBase:
    bl_label = 'Color Helper'
    bl_category = 'CH'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'HEADER_LAYOUT_EXPAND'}

    @classmethod
    def poll(self, context):
        return (
                (context.area.ui_type == 'VIEW_3D') or
                (hasattr(context.space_data, 'edit_tree') and
                 context.space_data.edit_tree and
                 context.space_data.edit_tree.bl_idname == 'ShaderNodeTree')
        )

    def draw_header(self, context):
        layout = self.layout
        layout.alignment = "RIGHT"
        layout.operator('ch.load_asset', icon='COLOR')
        layout.separator()

    def draw_palette_color(self, layout, palette, palette_index):
        row = layout.row(align=True)
        row.scale_y = 1.5
        for i, color in enumerate(palette.colors):
            col = row.column(align=True)
            col.prop(color, 'color')
            if palette.edit_mode:
                r = col.column(align=True)
                r.scale_y = 0.75
                remove = r.operator('ch.remove_color', icon='REMOVE', text='')
                remove.palette_index = palette_index
                remove.color_index = i

        row.operator('ch.add_color', icon='ADD',
                     text='' if len(palette.colors) != 0 else 'Add Color').palette_index = palette_index
        row.separator()
        row.prop(palette, 'edit_mode', icon='PREFERENCES', text='')

    def draw_ui(self, context, layout):

        if len(context.scene.ch_palette_collection) != 0:
            collection = context.scene.ch_palette_collection[context.scene.ch_palette_collection_index]

            row = layout.row()
            row.scale_y = 1.25
            row.scale_x = 1.5
            row.alignment = "RIGHT"
            row.separator()
            row.prop(context.scene, 'ch_palette_enum_collection', text='', icon='COLOR')

            row = row.row()
            row.scale_x = 0.9
            row.popover(panel='CH_PT_collection_manager', icon='PREFERENCES', text='')

            for i, palette in enumerate(collection.palettes):
                col = layout.column().box()
                row.operator_context = "INVOKE_DEFAULT"

                row = col.row(align=True)

                row.prop(palette, 'name', text='')
                row.separator()

                row.operator('ch.sort_color', icon='SORTSIZE', text='').palette_index = i
                row.operator('ch.hsv_palette', icon='MOD_HUE_SATURATION', text='').palette_index = i
                row.operator('ch.shuffle_palette', icon='CENTER_ONLY', text='').palette_index = i
                row.separator()

                row.prop(palette, 'node_group', text='')
                node_icon = 'ADD' if not palette.node_group else 'FILE_REFRESH'
                row.operator('ch.create_nodes_from_palette',
                             icon=node_icon, text='').palette_index = i
                row.separator()

                row.operator('ch.palette_extra_op_caller', icon='DOWNARROW_HLT', text='').palette_index = i

                row = col.row()
                self.draw_palette_color(row, palette, i)

        col = layout.column()
        col.scale_y = col.scale_x = 1.25

        col.box().operator('ch.add_palette', icon='ADD', emboss=False)

        row = col.row()
        row.operator('ch.create_palette_from_palette', icon='COLORSET_13_VEC')
        row.operator('ch.create_palette_from_clipboard', icon='PASTEDOWN')

    def draw(self, context):
        layout = self.layout

        self.draw_ui(context, layout)


class CH_PT_3d_view(SidePanelBase, bpy.types.Panel):
    bl_idname = 'CH_PT_3d_view'
    bl_space_type = 'VIEW_3D'


class CH_PT_node_editor(SidePanelBase, bpy.types.Panel):
    bl_idname = 'CH_PT_node_editor'
    bl_space_type = 'NODE_EDITOR'


class CH_MT_pop_menu(bpy.types.Menu):
    bl_label = "Color Helper"
    bl_idname = "CH_MT_pop_menu"

    @classmethod
    def poll(self, context):
        return (
                (context.area.ui_type == 'VIEW_3D') or
                (hasattr(context.space_data, 'edit_tree') and
                 context.space_data.edit_tree and
                 context.space_data.edit_tree.bl_idname == 'ShaderNodeTree')
        )

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.separator()
        pie.popover(panel='CH_PT_node_editor')


def draw_tool_bar(self, context):
    layout = self.layout
    col = layout.column()
    col.scale_y = 2
    col.popover(panel='CH_PT_node_editor', text='', icon='COLOR')


ui_panel = (
    CH_PT_node_editor,
    CH_PT_3d_view,
)


def register():
    bpy.utils.register_class(CH_OT_select_collection)
    bpy.utils.register_class(CH_MT_collection_switcher)
    bpy.utils.register_class(CH_PT_collection_manager)
    bpy.utils.register_class(CH_OT_palette_extra_op_caller)
    bpy.utils.register_class(CH_PT_node_editor)
    bpy.utils.register_class(CH_MT_pop_menu)

    # bpy.types.VIEW3D_PT_tools_active.append(draw_tool_bar)


def unregister():
    bpy.utils.unregister_class(CH_OT_select_collection)
    bpy.utils.unregister_class(CH_MT_collection_switcher)
    bpy.utils.unregister_class(CH_PT_collection_manager)
    bpy.utils.unregister_class(CH_OT_palette_extra_op_caller)
    bpy.utils.unregister_class(CH_PT_node_editor)
    bpy.utils.unregister_class(CH_MT_pop_menu)

    # bpy.types.VIEW3D_PT_tools_active.remove(draw_tool_bar)
