import bpy
from bpy.props import *


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
            layout.operator("ch.select_collection", text=item.name).index = i

        layout.separator()
        layout.label(text='Select Collection')


class CH_PT_node_editor(bpy.types.Panel):
    bl_idname = 'CH_PT_node_editor'
    bl_label = 'Color Helper'
    bl_category = 'Node'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'

    @classmethod
    def poll(self, context):
        return (
                (context.area.ui_type == 'VIEW_3D') or
                (hasattr(context.space_data, 'edit_tree') and
                 context.space_data.edit_tree and
                 context.space_data.edit_tree.bl_idname == 'ShaderNodeTree')
        )

    def draw_palette_color(self, layout, palette, palette_index):
        row = layout.row(align=True)
        row.scale_y = 1.5
        for i, color in enumerate(palette.colors):
            col = row.column(align=True)
            col.prop(color, 'color')
            if palette.edit_mode:
                remove = col.operator('ch.remove_color', icon='REMOVE', text='')
                remove.palette_index = palette_index
                remove.color_index = i

        row.operator('ch.add_color', icon='ADD', text='').palette_index = palette_index
        row.separator()
        row.prop(palette, 'edit_mode', icon='PREFERENCES', text='')

    def draw_ui(self,context,layout):
        if len(context.scene.ch_palette_collection) != 0:
            collection = context.scene.ch_palette_collection[context.scene.ch_palette_collection_index]

            row = layout.row()
            row.alignment = "RIGHT"
            row.scale_y = 1.25
            row.scale_x = 1.25
            row.separator()
            row.menu('CH_MT_collection_switcher', text=collection.name, icon='OUTLINER_COLLECTION')

            for i, palette in enumerate(collection.palettes):
                col = layout.column().box()

                row = col.row(align=True)

                if palette.edit_mode:
                    row_alert = row.row()
                    row_alert.alert = True
                    row_alert.operator('ch.remove_palette', icon='X', text='').palette_index = i

                row.prop(palette, 'name', text='')
                row.separator()

                row.operator('ch.sort_color', icon='SORTSIZE', text='').palette_index = i
                row.operator('ch.shuffle_palette', icon='CENTER_ONLY', text='').palette_index = i
                row.separator()

                row.prop(palette, 'node_group', text='')
                node_icon = 'ADD' if not palette.node_group else 'FILE_REFRESH'
                row.operator('ch.create_nodes_from_palette',
                             icon=node_icon, text='').palette_index = i
                row.separator()

                row.operator('ch.export_palette', icon='IMAGE_ZDEPTH', text='').palette_index = i

                row = col.row()
                self.draw_palette_color(row, palette, i)

        row = layout.row()
        row.scale_y = row.scale_x = 1.25
        row.operator('ch.add_palette', icon='ADD')
        row.operator('ch.create_palette_from_palette', icon='COLOR')
        row.operator('ch.create_palette_from_clipboard', icon='PASTEDOWN')

    def draw(self, context):
        layout = self.layout

        self.draw_ui(context,layout)


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
        pie.popover(panel = 'CH_PT_node_editor')


ui_panel = (
    CH_PT_node_editor
)


def register():
    bpy.utils.register_class(CH_OT_select_collection)
    bpy.utils.register_class(CH_MT_collection_switcher)
    bpy.utils.register_class(CH_PT_node_editor)
    bpy.utils.register_class(CH_MT_pop_menu)


def unregister():
    bpy.utils.unregister_class(CH_OT_select_collection)
    bpy.utils.unregister_class(CH_MT_collection_switcher)
    bpy.utils.unregister_class(CH_PT_node_editor)
    bpy.utils.unregister_class(CH_MT_pop_menu)
