import bpy
import os
from bpy.props import EnumProperty, StringProperty, CollectionProperty
from bpy_extras.io_utils import ExportHelper, ImportHelper
from ..preferences import get_pref


class CreatePaletteBase:

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

    def create_palette(self, palette):
        if len(bpy.context.scene.ch_palette_collection) == 0:
            collection = bpy.context.scene.ch_palette_collection.add()
            collection.name = 'Collection'
            bpy.context.scene.ch_palette_collection_index = 0

        collection = bpy.context.scene.ch_palette_collection[bpy.context.scene.ch_palette_collection_index]

        palette_item = collection.palettes.add()
        palette_item.name = 'Palettes' + str(len(collection.palettes))
        for i, color in enumerate(palette):
            clr = palette_item.colors.add()
            clr.color = color
        return palette_item

class CH_OT_create_palette_from_palette(CreatePaletteBase, bpy.types.Operator, ImportHelper):
    bl_idname = 'ch.create_palette_from_palette'
    bl_label = 'Platte From Palette Files'
    bl_options = {'UNDO_GROUPED'}

    filename_ext = ".png"

    files: CollectionProperty(type=bpy.types.PropertyGroup)

    filter_glob: StringProperty(
        default="*.png",
        options={'HIDDEN'}
    )

    def execute(self, context):
        from ..utils.process_image import extract_from_palette

        dirname = os.path.dirname(self.filepath)
        for f in self.files:
            image = bpy.data.images.load(os.path.join(dirname, f.name), check_existing=False)
            palette = extract_from_palette(image)

            palette_item = self.create_palette(palette)
            palette_item.name = f.name

            bpy.data.images.remove(image)
        return {'FINISHED'}


class CH_OT_create_palette_from_clipboard(CreatePaletteBase, bpy.types.Operator):
    bl_idname = 'ch.create_palette_from_clipboard'
    bl_label = 'Platte From Clipboard'
    bl_options = {'UNDO_GROUPED'}

    def execute(self, context):
        from ..utils.process_image import extract_from_image
        from ..utils.clipboard import Clipboard

        clipboard = Clipboard()
        filepath = clipboard.pull_image_from_clipboard()

        if not os.path.exists(filepath) or not os.path.isfile(filepath):
            return self._return(error_msg='Clipboard has no file')

        image = bpy.data.images.load(filepath, check_existing=False)
        channel_count = image.channels

        if image.file_format not in ['JPEG', 'PNG']:
            return self._return(error_msg=f'Currently, this only works for JPEG and PNG image files')
        if channel_count not in [3, 4]:
            return self._return(
                error_msg=f"This image has {channel_count} channels, but this method can only handle 3 or 4 channels")
        palette = extract_from_image(image,max_colors_to_return=get_pref().max_colors_return)

        self.create_palette(palette)

        bpy.data.images.remove(image)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(CH_OT_create_palette_from_palette)
    bpy.utils.register_class(CH_OT_create_palette_from_clipboard)


def unregister():
    bpy.utils.unregister_class(CH_OT_create_palette_from_palette)
    bpy.utils.unregister_class(CH_OT_create_palette_from_clipboard)
