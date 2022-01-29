import bpy
from bpy.props import IntProperty, BoolProperty, CollectionProperty, FloatVectorProperty, FloatProperty, EnumProperty

import random


class CH_OT_shuffle_palette(bpy.types.Operator):
    """Shuffle Palette Color"""
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

        context.area.tag_redraw()

        return {'FINISHED'}


def get_active_palette(palette_index):
    collection = bpy.context.scene.ch_palette_collection[bpy.context.scene.ch_palette_collection_index]
    src_palette = collection.palettes[palette_index]
    return src_palette


from bpy.types import PropertyGroup


class TempColorProps(PropertyGroup):
    color: FloatVectorProperty(
        subtype='COLOR', name='', min=0.0, max=1.0, size=4)


def update_hsv(self, context):
    src_palette = get_active_palette(self.palette_index)

    import colorsys
    src_colors_rgb = [color.color[:3] for color in src_palette.colors]
    src_colors_hsv = [colorsys.rgb_to_hsv(*rgb) for rgb in src_colors_rgb]

    new_colors_rgba = list()

    for hsv in src_colors_hsv:
        h = (hsv[0] + self.offset_h) % 1
        s = min(max(hsv[1] + self.offset_s, 0), 1)
        v = min(max(hsv[2] + self.offset_v, 0), 1)
        r, g, b = colorsys.hsv_to_rgb(h, s if hsv[1] != 0 else 0, v)
        new_colors_rgba.append((r, g, b, 1))

    for i, color_item in enumerate(self.temp_colors):
        color_item.color = new_colors_rgba[i]

    context.area.tag_redraw()


class CH_OT_hsv_palette(bpy.types.Operator):
    bl_idname = 'ch.hsv_palette'
    bl_label = 'Offset HSV'
    bl_options = {"INTERNAL", "UNDO_GROUPED"}

    palette_index: IntProperty()

    temp_colors: CollectionProperty(type=TempColorProps)
    src_palette = None

    offset_h: FloatProperty(name='Hue', default=0, max=0.5, min=-0.5, update=update_hsv)
    offset_s: FloatProperty(name='Saturation', default=0, max=1, min=-1, soft_max=0.5, soft_min=-0.5, update=update_hsv)
    offset_v: FloatProperty(name='Value', default=0, max=1, min=-1, soft_max=0.5, soft_min=-0.5, update=update_hsv)

    def invoke(self, context, event):
        collection = context.scene.ch_palette_collection[context.scene.ch_palette_collection_index]
        self.src_palette = collection.palettes[self.palette_index]

        self.temp_colors.clear()
        self.offset_h = self.offset_v = self.offset_s = 0

        for color_item in self.src_palette.colors:
            clr = self.temp_colors.add()
            clr.color = color_item.color

        return context.window_manager.invoke_props_dialog(self, width=context.region.width / 2)

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.scale_y = 1.5

        for color_item in self.temp_colors:
            row.prop(color_item, 'color')

        box = layout.box()
        box.label(text='Offset')
        col = box.column(align=True)
        col.use_property_split = True
        col.use_property_decorate = False

        col.prop(self, 'offset_h', slider=True)
        col.prop(self, 'offset_s', slider=True)
        col.prop(self, 'offset_v', slider=True)

    def apply_color(self):
        for i, color_item in enumerate(self.src_palette.colors):
            color_item.color = self.temp_colors[i].color

    def execute(self, context):
        self.apply_color()

        from .op_palette_manage import redraw_area
        redraw_area()

        return {"FINISHED"}


def update_sort(self, context):
    src_palette = get_active_palette(self.palette_index)

    import colorsys

    original_colors = sorted([
        (
            [(r, g, b)[int(self.mode)] for (r, g, b) in [colorsys.rgb_to_hsv(*color.color[:3])]],  # sort key
            tuple(color.color)  # source color
        ) for color in src_palette.colors], reverse=self.reverse
    )

    for new_index, (hsv, color) in enumerate(original_colors):
        self.temp_colors[new_index].color = color


class CH_OT_sort_color(bpy.types.Operator):
    bl_idname = 'ch.sort_color'
    bl_label = 'Sort Color'
    bl_options = {"INTERNAL", "UNDO_GROUPED"}

    palette_index: IntProperty()

    #
    temp_colors: CollectionProperty(type=TempColorProps)
    src_palette = None

    mode: EnumProperty(name='Mode', items=[
        ('0', 'Hue', ''),
        ('1', 'Saturation', ''),
        ('2', 'Value', ''),
    ], update=update_sort)

    reverse: BoolProperty(name='Reverse', default=False, update=update_sort)

    def apply_color(self):
        for i, color_item in enumerate(self.src_palette.colors):
            color_item.color = self.temp_colors[i].color

    def execute(self, context):
        self.apply_color()

        from .op_palette_manage import redraw_area
        redraw_area()

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.scale_y = 1.5

        for color_item in self.temp_colors:
            row.prop(color_item, 'color')

        box = layout.box()
        box.label(text='Offset')
        col = box.column(align=True)
        col.use_property_split = True
        col.use_property_decorate = False

        col.prop(self, 'mode', expand=True)
        col.prop(self, 'reverse')

    def invoke(self, context, event):
        collection = context.scene.ch_palette_collection[context.scene.ch_palette_collection_index]
        self.src_palette = collection.palettes[self.palette_index]

        self.temp_colors.clear()
        self.offset_h = self.offset_v = self.offset_s = 0

        for color_item in self.src_palette.colors:
            clr = self.temp_colors.add()
            clr.color = color_item.color

        # sort at first
        update_sort(self, context)

        return context.window_manager.invoke_props_dialog(self, width=context.region.width / 2)


def register():
    bpy.utils.register_class(CH_OT_shuffle_palette)
    bpy.utils.register_class(TempColorProps)
    bpy.utils.register_class(CH_OT_hsv_palette)
    bpy.utils.register_class(CH_OT_sort_color)


def unregister():
    bpy.utils.unregister_class(CH_OT_shuffle_palette)
    bpy.utils.unregister_class(TempColorProps)
    bpy.utils.unregister_class(CH_OT_hsv_palette)
    bpy.utils.unregister_class(CH_OT_sort_color)
