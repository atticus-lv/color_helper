# SPDX-FileCopyrightText: 2026 Atticus
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
import os
from bpy.props import (
    StringProperty,
    IntProperty,
)

from . import __folder_name__


def get_pref():
    """get preferences of this plugin"""
    return bpy.context.preferences.addons.get(__folder_name__).preferences


def change_panel_category():
    from .ui.panel import ui_panel

    for panel in ui_panel:
        if "bl_rna" in panel.__dict__:
            bpy.utils.unregister_class(panel)

    for panel in ui_panel:
        panel.bl_category = get_pref().category
        bpy.utils.register_class(panel)


def update_category(self, context):
    try:
        change_panel_category()

    except(Exception) as e:
        self.report({'ERROR'}, f'Category change failed:\n{e}')


def load_asset():
    from .utils.process_image import extract_from_palette

    base_dir = get_pref().asset_lib
    if not base_dir:
        return None

    base_dir = bpy.path.abspath(base_dir)
    if not os.path.isdir(base_dir):
        return None

    loaded_count = 0
    image_extensions = {'.png', '.jpg', '.jpeg'}

    for file in os.listdir(base_dir):
        image_dir = os.path.join(base_dir, file)

        if not os.path.isdir(image_dir): continue
        if file in bpy.context.scene.ch_palette_collection:
            coll_item = bpy.context.scene.ch_palette_collection.get(file)
        else:
            coll_item = bpy.context.scene.ch_palette_collection.add()
            coll_item.name = file

        # search sub folder
        for img_name in os.listdir(image_dir):
            # check exist
            base, sep, ext = img_name.rpartition('.')
            if f'.{ext.lower()}' not in image_extensions:
                continue

            if base not in coll_item.palettes:
                image = None
                try:
                    image = bpy.data.images.load(os.path.join(image_dir, img_name), check_existing=False)
                    # add palette
                    palette_item = coll_item.palettes.add()
                    palette_item.name = base
                    palette_item.hide = True
                    # add color
                    palette = extract_from_palette(image)
                    for i, color in enumerate(palette):
                        clr = palette_item.colors.add()
                        clr.color = color
                    loaded_count += 1
                finally:
                    if image is not None:
                        bpy.data.images.remove(image)

        if len(coll_item.palettes) == 0: bpy.context.scene.ch_palette_collection.remove(-1)
    # redraw
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw()
    return base_dir, loaded_count


def update_asset(self, context):
    load_asset()


class CH_Preference(bpy.types.AddonPreferences):
    bl_idname = __package__

    category: StringProperty(name="Category", default="CH", update=update_category)
    column_count: IntProperty(name='Column', default=5, min=4)

    max_colors_return:IntProperty(name = 'Max Color Return',default=5,min=3)
    # asset
    asset_lib: StringProperty(
        name='Palette Library Folder',
        description='Optional folder containing palette image subfolders to import',
        subtype='DIR_PATH',
    )

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.scale_y = 1.2
        col.prop(self, 'category', icon='ALIGN_MIDDLE')
        col.prop(self, 'asset_lib', icon='COLOR')
        col.separator()
        # col.prop(self, 'column_count')
        col.prop(self, 'max_colors_return')


class CH_OT_load_asset(bpy.types.Operator):
    bl_idname = 'ch.load_asset'
    bl_label = 'Load Palette Library'

    def execute(self, context):
        result = load_asset()

        if result is None:
            self.report({'INFO'}, 'No palette library folder is set')
            return {'FINISHED'}

        base_dir, loaded_count = result
        self.report({'INFO'}, f'Loaded {loaded_count} palette images from {base_dir}')
        return {'FINISHED'}


classes = [
    CH_Preference,
    CH_OT_load_asset,
]

addon_keymaps = []


def add_keybind():
    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'C', 'PRESS', alt=True)
        kmi.properties.name = "CH_MT_pop_menu"
        addon_keymaps.append((km, kmi))

        km = wm.keyconfigs.addon.keymaps.new(name='Node Editor', space_type='NODE_EDITOR')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'C', 'PRESS', alt=True)
        kmi.properties.name = "CH_MT_pop_menu"
        addon_keymaps.append((km, kmi))


def remove_keybind():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)

    addon_keymaps.clear()


def register():
    add_keybind()

    for cls in classes:
        bpy.utils.register_class(cls)

    try:
        change_panel_category()

    except(Exception) as e:
        print(e)


def unregister():
    remove_keybind()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
