# SPDX-FileCopyrightText: 2026 Atticus
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.props import IntProperty


def resolve_rna_path(path):
    if path.startswith('bpy.context.'):
        return bpy.context.path_resolve(path[len('bpy.context.'):])

    if path.startswith('bpy.data.'):
        data_path = path[len('bpy.data.'):]
        split_index = min(
            (index for index in (data_path.find('.'), data_path.find('[')) if index != -1),
            default=len(data_path),
        )
        collection_name = data_path[:split_index]
        data_path = data_path[split_index:]
        if data_path.startswith('.'):
            data_path = data_path[1:]
        collection = getattr(bpy.data, collection_name)
        if not data_path:
            return collection
        if not data_path.startswith('['):
            raise ValueError(f'Unsupported bpy.data path: {path}')

        item_end = data_path.find(']')
        item_key = data_path[1:item_end]
        if item_key.startswith(("'", '"')) and item_key.endswith(("'", '"')):
            item_key = item_key[1:-1]
        else:
            item_key = int(item_key)

        data_block = collection[item_key]
        data_path = data_path[item_end + 1:]
        if data_path.startswith('.'):
            data_path = data_path[1:]
        return data_block.path_resolve(data_path) if data_path else data_block

    raise ValueError(f'Unsupported RNA path: {path}')


class CH_OT_paste_and_add_color(bpy.types.Operator):
    """Paste hex/rgb string from clipboard with Gamma correct"""
    bl_idname = 'ch.paste_and_add_color'
    bl_label = 'Paste and Add Color'
    bl_options = {'INTERNAL', 'UNDO_GROUPED'}

    palette_index: IntProperty()

    def execute(self, context):
        clipboard = context.window_manager.clipboard
        if not isinstance(clipboard, str): return {'CANCELLED'}
        clipboard.encode('utf8')

        from ..utils.color_correct import Str2Color
        CP = Str2Color(clipboard)
        if not CP.bl_color: return {'CANCELLED'}

        collection = context.scene.ch_palette_collection[context.scene.ch_palette_collection_index]
        palette = collection.palettes[self.palette_index]

        color_item = palette.colors.add()
        try:
            setattr(color_item, 'color', CP.bl_color)
        except ValueError:
            setattr(color_item, 'color', CP.bl_color[:3])

        return {"FINISHED"}


class CH_OT_paste_color(bpy.types.Operator):
    """Paste hex/rgb string from clipboard with Gamma correct to blender"""
    bl_idname = "ch.color_paster"
    bl_label = "Paste Color"
    bl_options = {'INTERNAL', 'UNDO_GROUPED'}

    @classmethod
    def poll(cls, context):
        return bpy.ops.ui.copy_data_path_button.poll()

    def execute(self, context):
        clipboard = context.window_manager.clipboard
        if not isinstance(clipboard, str): return {'CANCELLED'}
        clipboard.encode('utf8')

        from ..utils.color_correct import Str2Color
        CP = Str2Color(clipboard)
        if not CP.bl_color: return {'CANCELLED'}

        # get property that need to paste
        bpy.ops.ui.copy_data_path_button(full_path=True)
        full_path = context.window_manager.clipboard
        rna, prop = full_path.rsplit('.', 1)
        data_block = resolve_rna_path(rna)
        # some property only accept rgb values
        try:
            try:
                setattr(data_block, prop, CP.bl_color)
            except ValueError:
                setattr(data_block, prop, CP.bl_color[:3])
        except Exception as e:
            print(f'Paste Color Error:{e}')
        finally:  # restore clip board
            context.window_manager.clipboard = clipboard

        return {'FINISHED'}


def context_menu_func(self, context):
    if CH_OT_paste_color.poll(context):
        layout = self.layout
        layout.separator()
        layout.operator('ch.color_paster', icon='PASTEDOWN')
        layout.separator()


class WM_MT_button_context(bpy.types.Menu):
    bl_label = "WM_MT_button context"

    def draw(self, context):
        pass


def add_menu():
    bpy.utils.register_class(WM_MT_button_context)
    bpy.types.WM_MT_button_context.append(context_menu_func)


def register():
    bpy.utils.register_class(CH_OT_paste_color)
    bpy.utils.register_class(CH_OT_paste_and_add_color)

    if bpy.app.version < (3, 1, 0):
        if not hasattr(bpy.types, 'WM_MT_button_context'):
            add_menu()
    else:
        add_menu()


def unregister():
    bpy.utils.unregister_class(CH_OT_paste_color)
    bpy.utils.unregister_class(CH_OT_paste_and_add_color)

    if hasattr(bpy.types, "WM_MT_button_context"):
        bpy.types.WM_MT_button_context.remove(context_menu_func)
