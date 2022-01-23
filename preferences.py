import bpy
import os
from bpy.props import (EnumProperty,
                       StringProperty,
                       BoolProperty,
                       CollectionProperty,
                       IntProperty,
                       FloatProperty,
                       PointerProperty)
from bpy.types import PropertyGroup

from . import __folder_name__
import rna_keymap_ui


def get_pref():
    """get preferences of this plugin"""
    return bpy.context.preferences.addons.get(__folder_name__).preferences


def update_category(self, context):
    from .ui.panel_node_editor import ui_panel

    try:
        for panel in ui_panel.panels:
            if "bl_rna" in panel.__dict__:
                bpy.utils.unregister_class(panel)

        for panel in ui_panel.panels:
            panel.bl_category = get_pref().category
            bpy.utils.register_class(panel)

    except(Exception) as e:
        self.report({'ERROR'}, f'Category change failed:\n{e}')


class CH_Preference(bpy.types.AddonPreferences):
    bl_idname = __package__

    category: StringProperty(name="Category", default="SPIO", update=update_category)
    directory: StringProperty(name='Export', subtype='DIR_PATH')

    def draw(self, context):
        layout = self.layout

        col = layout.row(align=True)
        col.scale_y = 1.2
        col.prop(self, 'category')
        col.prop(self, 'directory')


classes = [
    CH_Preference
]

addon_keymaps = []


def add_keybind():
    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        pass
        # km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        # kmi = km.keymap_items.new("wm.super_import", 'V', 'PRESS', ctrl=True, shift=True)
        # addon_keymaps.append((km, kmi))
        #
        # km = wm.keyconfigs.addon.keymaps.new(name='Node Editor', space_type='NODE_EDITOR')
        # kmi = km.keymap_items.new("wm.super_import", 'V', 'PRESS', ctrl=True, shift=True)
        # addon_keymaps.append((km, kmi))
        #
        # km = wm.keyconfigs.addon.keymaps.new(name='Image Generic', space_type='IMAGE_EDITOR')
        # kmi = km.keymap_items.new("wm.super_export", 'C', 'PRESS', ctrl=True, shift=True)
        # addon_keymaps.append((km, kmi))
        #
        # km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        # kmi = km.keymap_items.new("wm.super_export", 'C', 'PRESS', ctrl=True, shift=True)
        # addon_keymaps.append((km, kmi))


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


def unregister():
    remove_keybind()

    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.WindowManager.spio_filter
