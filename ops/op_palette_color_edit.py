import bpy
from bpy.props import IntProperty, BoolProperty, CollectionProperty, FloatVectorProperty, FloatProperty, EnumProperty

from bpy.types import PropertyGroup

import random
from mathutils import Color


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


class TempColorProps(PropertyGroup):
    color: FloatVectorProperty(
        subtype='COLOR', name='', min=0, soft_max=1, size=4)


history_colors = []


def update_hsv(self, context):
    global history_colors

    import colorsys

    if len(history_colors) == 0:
        src_colors_rgb = [color_item.color[:3] for color_item in self.temp_colors]
        history_colors = src_colors_rgb

    src_colors_hsv = [colorsys.rgb_to_hsv(*rgb) for rgb in history_colors]
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


def update_sort(self, context):
    import colorsys

    original_colors = sorted([
        (
            [(r, g, b)[int(self.mode)] for (r, g, b) in [colorsys.rgb_to_hsv(*color.color[:3])]],  # sort key
            tuple(color.color)  # source color
        ) for color in self.temp_colors], reverse=self.reverse
    )

    for new_index, (hsv, color) in enumerate(original_colors):
        self.temp_colors[new_index].color = color


def hsv_2_rgba(c):
    """blender style hsv to rgba"""
    return (c.r, c.g, c.b, 1)


def get_base_color(self):
    c = Color()
    import colorsys
    c.hsv = colorsys.rgb_to_hsv(*self.base_color[:3])
    return c


def shuffle_colors(colors):
    shuffled_colors = [tuple(c.color) for c in colors]
    random.shuffle(shuffled_colors)

    for i, color in enumerate(shuffled_colors):
        colors[i].color = color


def update_Monochromatic(self, c: Color):
    base_hue = c.h
    base_sat = c.s
    base_val = c.v

    offset_val = base_val + 0.3 if base_val < 0.7 else base_val - 0.5
    offset_val2 = base_val - 0.4 if base_val > 0.4 else base_val + 0.6

    offset_sat = base_sat - 0.3 if base_sat > 0.4 else base_sat + 0.3

    color_1 = Color()
    color_2 = Color()
    color_3 = Color()
    color_4 = Color()
    color_5 = Color()

    color_1.hsv = base_hue, base_sat, max(0.3, offset_val)
    color_2.hsv = base_hue, max(0.3, offset_sat), max(0.2, base_val)
    color_3.hsv = base_hue, base_sat, base_val
    color_4.hsv = base_hue, max(0.3, offset_sat), max(0.3, offset_val)
    color_5.hsv = base_hue, base_sat, offset_val2

    self.temp_colors[0].color = hsv_2_rgba(color_1)
    self.temp_colors[1].color = hsv_2_rgba(color_2)
    self.temp_colors[2].color = hsv_2_rgba(color_3)
    self.temp_colors[3].color = hsv_2_rgba(color_4)
    self.temp_colors[4].color = hsv_2_rgba(color_5)


def update_Analogous(self, c: Color):
    # Analogous
    offset = self.slider_Analogous_offset

    base_hue = c.h
    base_sat = c.s
    base_val = c.v

    start_hue = base_hue - 2 * offset
    for i in range(0, 5):
        hue = start_hue + offset * i

        if hue < 0:
            hue = 1 + hue
        elif hue > + 1:
            hue = 1 - hue

        new_color = Color()
        new_color.hsv = hue, base_sat, base_val
        self.temp_colors[i].color = hsv_2_rgba(new_color)


def update_Complementary(self, c: Color):
    base_hue = c.h
    base_sat = c.s
    base_val = c.v

    offset_val = base_val + 0.3 if base_val < 0.5 else base_val - 0.3
    offset_hue = base_hue + 0.5

    if offset_hue < 0:
        offset_hue = 1 + offset_hue
    elif offset_hue > + 1:
        offset_hue = 1 - offset_hue

    color_1 = Color()
    color_2 = Color()
    color_3 = Color()
    color_4 = Color()
    color_5 = Color()

    color_1.hsv = base_hue, max(base_sat + 0.1, 0.1), offset_val
    color_2.hsv = base_hue, max(base_sat - 0.1, 0), min(base_val + 0.3, 1)
    color_3.hsv = base_hue, base_sat, base_val
    color_4.hsv = offset_hue, max(base_sat, 0.2), offset_val
    color_5.hsv = offset_hue, base_sat, base_val

    self.temp_colors[0].color = hsv_2_rgba(color_1)
    self.temp_colors[1].color = hsv_2_rgba(color_2)
    self.temp_colors[2].color = hsv_2_rgba(color_3)
    self.temp_colors[3].color = hsv_2_rgba(color_4)
    self.temp_colors[4].color = hsv_2_rgba(color_5)


def restore(self):
    self.offset_h = 0
    self.offset_s = 0
    self.offset_v = 0

    global history_colors
    history_colors.clear()


def refresh_base_color(self, context):
    self.base_color = (random.random(), random.random(), random.random(), 1)


def update_generator(self, context):
    restore(self)

    if self.generate_color:
        # clear color
        self.temp_colors.clear()
        for color_item in range(0, 5):
            clr = self.temp_colors.add()
            clr.color = (1, 1, 1, 1)
        # generate_method
        c = get_base_color(self)
        if self.generate_method == 'ANALOGOUS':
            update_Analogous(self, c)
        elif self.generate_method == 'MONOCHROMATIC':
            update_Monochromatic(self, c)
        elif self.generate_method == 'COMPLEMENTARY':
            update_Complementary(self, c)

    else:
        # restore from source palette
        collection = context.scene.ch_palette_collection[context.scene.ch_palette_collection_index]
        src_palette = collection.palettes[self.palette_index]

        self.temp_colors.clear()
        self.offset_h = self.offset_v = self.offset_s = 0

        for color_item in src_palette.colors:
            clr = self.temp_colors.add()
            clr.color = color_item.color

    from .op_palette_manage import redraw_area
    redraw_area()


PALETTE_HISTORY = []


class CH_OT_edit_color(bpy.types.Operator):
    """Create, Offset, Sort Palette Colors"""
    bl_idname = 'ch.edit_color'
    bl_label = 'Edit Mode'
    bl_options = {"INTERNAL", "UNDO"}

    temp_colors: CollectionProperty(type=TempColorProps)
    src_palette = None
    palette_index: IntProperty()

    # color generate
    #################
    generate_color: BoolProperty(name='Generate', update=update_generator)
    generate_method: EnumProperty(name='Method',
                                  items=[
                                      ('ANALOGOUS', 'Analogous', ''),
                                      ('MONOCHROMATIC', 'Monochromatic', ''),
                                      ('COMPLEMENTARY', 'Complementary', ''),
                                  ], update=update_generator)

    base_color: FloatVectorProperty(subtype='COLOR', size=4, min=0, max=1, default=(0.48, 0.6, 0, 1),
                                    update=update_generator)

    refresh: BoolProperty(name='Refresh', update=refresh_base_color)

    # Analogous
    slider_Analogous_offset: FloatProperty(name='Offset', min=0, max=0.2, default=0.1,
                                           update=update_generator)  # 5 color 4 step

    ###############
    # global offset hsv
    offset_h: FloatProperty(name='Hue', default=0, max=0.5, min=-0.5, update=update_hsv)
    offset_s: FloatProperty(name='Saturation', default=0, max=1, min=-1, soft_max=0.5, soft_min=-0.5, update=update_hsv)
    offset_v: FloatProperty(name='Value', default=0, max=1, min=-1, soft_max=0.5, soft_min=-0.5, update=update_hsv)

    # sort
    mode: EnumProperty(name='Mode', items=[
        ('0', 'Hue', ''),
        ('1', 'Saturation', ''),
        ('2', 'Value', ''),
    ], update=update_sort)
    reverse: BoolProperty(name='Reverse', default=False, update=update_sort)

    @classmethod
    def poll(cls, context):
        return (
                (context.area.ui_type == 'VIEW_3D') or
                (hasattr(context.space_data, 'edit_tree') and
                 context.space_data.edit_tree and
                 context.space_data.edit_tree.bl_idname == 'ShaderNodeTree')
        )

    def invoke(self, context, event):
        # restore
        global history_colors
        history_colors.clear()
        restore(self)

        collection = context.scene.ch_palette_collection[context.scene.ch_palette_collection_index]
        self.src_palette = collection.palettes[self.palette_index]

        self.temp_colors.clear()
        self.offset_h = self.offset_v = self.offset_s = 0

        for color_item in self.src_palette.colors:
            clr = self.temp_colors.add()
            clr.color = color_item.color

        return context.window_manager.invoke_props_dialog(self, width=int(context.region.width / 2))

    def apply_color(self):
        if not self.generate_color:
            for i, color_item in enumerate(self.src_palette.colors):
                color_item.color = self.temp_colors[i].color
        else:
            self.src_palette.colors.clear()
            for i in range(0, 5):
                clr = self.src_palette.colors.add()
                clr.color = self.temp_colors[i].color

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.scale_y = 1.5
        for color_item in self.temp_colors:
            row.prop(color_item, 'color')

        box = layout.box()
        box.prop(self, 'generate_color')
        if self.generate_color:
            box.prop(self, 'generate_method')
            row = box.row(align=True)
            row.prop(self, 'base_color', text='')
            row.prop(self, 'refresh', emboss=False, toggle=True, icon='FILE_REFRESH', text='')

            # Analogous
            if self.generate_method == 'ANALOGOUS':
                box.prop(self, 'slider_Analogous_offset', slider=True)

        box = layout.box()
        box.label(text='Offset')
        col = box.column(align=True)
        col.use_property_split = True
        col.use_property_decorate = False

        col.prop(self, 'offset_h', slider=True)
        col.prop(self, 'offset_s', slider=True)
        col.prop(self, 'offset_v', slider=True)

        box = layout.box()
        box.label(text='Sort')
        col = box.column(align=True)
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(self, 'mode', expand=True)
        col.prop(self, 'reverse')

    def execute(self, context):
        self.apply_color()
        self.generate_color = False

        return {'FINISHED'}


def register():
    bpy.utils.register_class(CH_OT_shuffle_palette)
    bpy.utils.register_class(TempColorProps)
    bpy.utils.register_class(CH_OT_edit_color)


def unregister():
    bpy.utils.unregister_class(CH_OT_shuffle_palette)
    bpy.utils.unregister_class(TempColorProps)
    bpy.utils.unregister_class(CH_OT_edit_color)
