import bpy
from bpy.props import IntProperty, BoolProperty

import random


class CH_OT_shuffle_palette(bpy.types.Operator):
    """Shift to update node group binding together """
    bl_idname = "ch.shuffle_palette"
    bl_label = "Shuffle Colors"
    bl_options = {'UNDO_GROUPED'}

    palette_index: IntProperty()
    update_node: BoolProperty(default=False)

    def invoke(self, context, event):
        collection = context.scene.ch_palette_collection[context.scene.ch_palette_collection_index]
        palette = collection.palettes[self.palette_index]

        shuffled_colors = [tuple(c.color) for c in palette.colors]
        random.shuffle(shuffled_colors)

        for i, color in enumerate(shuffled_colors):
            palette.colors[i].color = color

        if event.shift:
            bpy.ops.ch.create_nodes_from_palette('INVOKE_DEFAULT',palette_index=self.palette_index)

        context.area.tag_redraw()

        return {'FINISHED'}



def register():
    bpy.utils.register_class(CH_OT_shuffle_palette)


def unregister():
    bpy.utils.unregister_class(CH_OT_shuffle_palette)
