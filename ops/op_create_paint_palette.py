import bpy
from bpy.props import IntProperty


class CH_OT_create_paint_palette(bpy.types.Operator):
    """Create a new paint palette"""
    bl_idname = "ch.create_paint_palette"
    bl_label = "Create Paint Palette"
    bl_options = {'REGISTER', 'UNDO'}

    palette_index: IntProperty(options={'HIDDEN'})

    def execute(self, context):
        collection = context.scene.ch_palette_collection[context.scene.ch_palette_collection_index]
        palette = collection.palettes[self.palette_index]

        if palette.name + '_paint' in bpy.data.palettes:
            bpy.data.palettes.remove(bpy.data.palettes[palette.name])

        p = bpy.data.palettes.new(palette.name + '_paint')

        for color_item in palette.colors:
            c = color_item.color[:3]
            new_color = p.colors.new()
            new_color.color = c

        self.report({'INFO'}, "Paint palette created")

        return {'FINISHED'}


def register():
    bpy.utils.register_class(CH_OT_create_paint_palette)


def unregister():
    bpy.utils.unregister_class(CH_OT_create_paint_palette)
