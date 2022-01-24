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


def change_panel_category():
    from .ui.panel_node_editor import ui_panel

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
    import os
    from .utils.process_image import extract_from_palette

    base_dir = get_pref().asset_lib
    print('Load Color Helper Asset: ', base_dir)
    if not (os.path.exists(base_dir) and os.path.isdir(base_dir)): return

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

            if base not in coll_item.palettes:
                image = bpy.data.images.load(os.path.join(image_dir, img_name), check_existing=False)
                # add palette
                palette_item = coll_item.palettes.add()
                palette_item.name = base
                # add color
                palette = extract_from_palette(image)
                for i, color in enumerate(palette):
                    clr = palette_item.colors.add()
                    clr.color = color
                # clear temp
                bpy.data.images.remove(image)

        if len(coll_item.palettes) == 0: bpy.context.scene.ch_palette_collection.remove(-1)


def update_asset(self, context):
    load_asset()


class CH_Preference(bpy.types.AddonPreferences):
    bl_idname = __package__

    category: StringProperty(name="Category", default="CH", update=update_category)
    directory: StringProperty(name='Export Directory', subtype='DIR_PATH')

    asset_lib: StringProperty(name='Asset Library', subtype='DIR_PATH', update=update_asset)

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.scale_y = 1.2
        col.prop(self, 'category', icon='ALIGN_MIDDLE')
        col.prop(self, 'directory', icon='EXPORT')
        col.prop(self, 'asset_lib', icon='COLOR')


class CH_OT_load_asset(bpy.types.Operator):
    bl_idname = 'ch.load_asset'
    bl_label = 'Load Asset'

    def execute(self, context):
        load_asset()
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

    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.WindowManager.spio_filter
