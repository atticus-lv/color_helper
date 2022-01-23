import bpy
from bpy.props import *


def rgb_to_hsv(r, g, b):
    maxc = max(r, g, b)
    minc = min(r, g, b)
    v = maxc
    if minc == maxc:
        return 0.0, 0.0, v
    s = (maxc - minc) / maxc
    rc = (maxc - r) / (maxc - minc)
    gc = (maxc - g) / (maxc - minc)
    bc = (maxc - b) / (maxc - minc)
    if r == maxc:
        h = bc - gc
    elif g == maxc:
        h = 2.0 + rc - bc
    else:
        h = 4.0 + gc - rc
    h = (h / 6.0) % 1.0
    return h, s, v


def hsv_to_rgb(h, s, v):
    if s == 0.0:
        return v, v, v
    i = int(h * 6.0)  # XXX assume int() truncates!
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6
    if i == 0:
        return v, t, p
    if i == 1:
        return q, v, p
    if i == 2:
        return p, v, t
    if i == 3:
        return p, q, v
    if i == 4:
        return t, p, v
    if i == 5:
        return v, p, q


class CH_OT_remove_palette(bpy.types.Operator):
    bl_idname = 'ch.remove_palette'
    bl_label = 'Remove Palette'

    palette_index: IntProperty()

    def execute(self, context):
        collection = context.scene.ch_palette_collection[context.scene.ch_palette_collection_index]
        collection.palettes.remove(self.palette_index)

        return {'FINISHED'}


class CH_OT_add_palette(bpy.types.Operator):
    bl_idname = 'ch.add_palette'
    bl_label = 'Add Palette'

    palette_index: IntProperty()

    def execute(self, context):
        if len(context.scene.ch_palette_collection) == 0:
            collection = context.scene.ch_palette_collection.add()
            collection.name = 'Collection'
        else:
            collection = context.scene.ch_palette_collection[context.scene.ch_palette_collection_index]

        item = collection.palettes.add()

        item.name = 'Palette' + str(len(collection.palettes))

        return {'FINISHED'}


class CH_OT_sort_color(bpy.types.Operator):
    bl_idname = 'ch.sort_color'
    bl_label = 'Sort Color'

    mode: EnumProperty(name='Mode', items=[
        ('0', 'Hue', ''),
        ('1', 'Saturation', ''),
        ('2', 'Value', ''),
    ])

    reverse: BoolProperty(name='Reverse', default=False)

    palette_index: IntProperty()

    def execute(self, context):
        collection = context.scene.ch_palette_collection[context.scene.ch_palette_collection_index]
        palette = collection.palettes[self.palette_index]

        original_colors = sorted([
            (
                [(r, g, b)[int(self.mode)] for (r, g, b) in [rgb_to_hsv(*color.color[:3])]], # sort key
                tuple(color.color) # source color
            ) for color in palette.colors], reverse=self.reverse
        )

        for new_index, (hsv, color) in enumerate(original_colors):
            palette.colors[new_index].color = color

        context.area.tag_redraw()

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'mode',expand = True)
        layout.prop(self, 'reverse')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self,width = 200  )


class CH_OT_add_color(bpy.types.Operator):
    bl_idname = 'ch.add_color'
    bl_label = 'Add Color'

    palette_index: IntProperty()
    color_index: IntProperty()

    def execute(self, context):
        collection = context.scene.ch_palette_collection[context.scene.ch_palette_collection_index]
        palette = collection.palettes[self.palette_index]

        item = palette.colors.add()
        item.color = (1, 1, 1, 1)

        return {'FINISHED'}


class CH_OT_remove_color(bpy.types.Operator):
    bl_idname = 'ch.remove_color'
    bl_label = 'Remove Color'

    palette_index: IntProperty()
    color_index: IntProperty()

    def execute(self, context):
        collection = context.scene.ch_palette_collection[context.scene.ch_palette_collection_index]
        palette = collection.palettes[self.palette_index]

        palette.colors.remove(self.color_index)

        return {'FINISHED'}


classes = (
    CH_OT_add_palette,
    CH_OT_remove_palette,

    CH_OT_sort_color,

    CH_OT_add_color,
    CH_OT_remove_color
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
