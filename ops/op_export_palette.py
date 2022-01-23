import bpy
import os
from bpy.props import *

COLOR_WIDTH = 50
COLOR_HEIGHT = 50


def make_png_from_palette(palette, save_path=None):
    from ..utils.process_image import gamma_invert
    colors = [[gamma_invert(c) for c in color.color] for color in palette.colors]

    pixels = []
    for color in colors:
        pixels += list(color) * COLOR_WIDTH
    pixels *= COLOR_HEIGHT

    image_width = len(colors) * COLOR_WIDTH
    image = bpy.data.images.new(palette.name, width=image_width, height=COLOR_HEIGHT)
    image.pixels = pixels

    if save_path:
        image.filepath_raw = save_path

    image.file_format = 'PNG'

    return image


class CH_OT_export_palette(bpy.types.Operator):
    bl_idname = 'ch.export_palette'
    bl_label = 'Export Palette'
    bl_options = {"REGISTER", "UNDO"}

    palette_index: IntProperty(options={'HIDDEN'})

    def execute(self, context):
        collection = context.scene.ch_palette_collection[context.scene.ch_palette_collection_index]
        palette = collection.palettes[self.palette_index]

        image = make_png_from_palette(palette)

        bpy.ops.screen.userpref_show()
        bpy.ops.screen.region_flip('INVOKE_AREA')
        area = bpy.context.window_manager.windows[-1].screen.areas[0]
        # Change area type
        area.type = "IMAGE_EDITOR"
        bpy.context.space_data.image = image

        return {'FINISHED'}


from bpy_extras.io_utils import ExportHelper


class CH_OT_batch_export_palette(bpy.types.Operator):
    bl_idname = 'ch.batch_export_palette'
    bl_label = 'Export Collection Palette'
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        from ..preferences import get_pref
        directory = get_pref().directory
        if not (os.path.exists(directory) and os.path.isdir(directory)):
            self.report({"ERROR"}, 'Define your export dir in preference first!')
            return {'CANCELLED'}

        collection = context.scene.ch_palette_collection[context.scene.ch_palette_collection_index]
        for palette in collection.palettes:
            filepath = os.path.join(self.directory, palette.name) + '.png'
            image = make_png_from_palette(palette, save_path=filepath)
            image.save()
            bpy.data.images.remove(image)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(CH_OT_export_palette)
    bpy.utils.register_class(CH_OT_batch_export_palette)


def unregister():
    bpy.utils.unregister_class(CH_OT_export_palette)
    bpy.utils.unregister_class(CH_OT_batch_export_palette)
