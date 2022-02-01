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
        subtype='COLOR', name='', min=0.0, max=1.0, size=4)


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


def add_alpha(c):
    rgb = list(c)
    return (rgb[0], rgb[1], rgb[2], 1)


def get_base_color(self):
    c = Color()
    c.hsv = 1.0, 0.0, 1.0
    index = [0, 1, 2, 3, 4]
    random.shuffle(index)
    c.hsv = random.random(), random.random(), random.random()
    if random.randint(0, 3) / 2 == 0:
        c.h = 0.0
    if c.v >= 0.95:
        c.v = c.v - 0.1
    elif c.v <= 0.4:
        c.v = c.v + 0.2

    import colorsys
    if self.use_custom_color:
        if colorsys.rgb_to_hsv(*self.custom_base_color[:3]) != (0.0, 0.0, 0.0):
            for i, rgb in enumerate(list(c)):
                c[i] = random.uniform(self.custom_base_color[i] - 0.1, self.custom_base_color[i] + 0.05)
    return c


def shuffle_colors(colors):
    shuffled_colors = [tuple(c.color) for c in colors]
    random.shuffle(shuffled_colors)

    for i, color in enumerate(shuffled_colors):
        colors[i].color = color


def update_Monochromatic(self, c: Color):
    hue = c.h
    sat_less = 0.0
    if c.s <= 0.1:
        sat_less = 0.0
    else:
        sat_less = random.uniform(0.1, c.s)

    if sat_less == c.s:
        sat_less = random.uniform(0.1, c.s)

    if sat_less < 0.25:
        sat_less = 0.4

    sat_more = random.uniform(c.s + 0.1, c.s + 0.2)

    val_less = random.uniform(0.2, c.v)
    val_more = random.uniform(c.v + 0.1, c.v + 0.3)

    if val_less == 0.0:
        val_less = 0.3
    elif val_more == 0.0:
        val_more = 0.7

    c1 = Color()
    c1.hsv = hue, sat_more, val_more

    self.temp_colors[0].color = add_alpha(c1)

    c1.hsv = hue, sat_more + 0.1, val_more
    self.temp_colors[1].color = add_alpha(c1)

    c1.hsv = hue, c.s, c.v
    self.temp_colors[2].color = add_alpha(c1)

    c1.hsv = hue, sat_more + 0.1, val_less - 0.1
    self.temp_colors[3].color = add_alpha(c1)

    c1.hsv = hue, sat_less, val_less - 0.1
    self.temp_colors[4].color = add_alpha(c1)

    shuffle_colors(self.temp_colors)


def update_Analogous(self, c: Color):
    # Analogous
    sat = random.uniform(c.s, 1)
    if sat <= 0.4:
        sat = sat + 0.35
    val = c.v
    if (val <= 1.0 or val > 1.0) and val >= 0.8:
        val = val - 0.1
    if val <= 0.3:
        val = 0.7
    val1 = random.uniform(val + 0.1, val + 0.25)
    if (val1 <= 1.0 or val1 > 1.0) and val1 >= 0.8:
        val1 = val1 - 0.3
    if val1 <= 0.3:
        val1 = 0.7
    hue1 = random.uniform(c.h + 0.2, c.h + 0.3)
    hue = random.uniform(c.h, c.h + 0.2)
    if hue1 == hue:
        hue1 = hue1 - 0.1
    if hue == 0:
        hue1 = 0.1
    c2 = Color()
    c2.hsv = hue1, sat - 0.2, val

    self.temp_colors[2].color = add_alpha(c2)

    Hue1_2 = random.uniform(c.h - 0.07, c.h - 0.2)
    if Hue1_2 == hue1:
        Hue1_2 = Hue1_2 - 0.1
    c2.hsv = hue, sat + 0.2, val1
    self.temp_colors[0].color = add_alpha(c2)
    self.temp_colors[4].color = add_alpha(c2)

    Hue_1 = random.uniform(c.h, c.h - 0.3)
    if Hue_1 == 0:
        Hue_1 = 0.9
    if Hue_1 == hue:
        Hue_1 = Hue_1 - 0.08
    if c.h == 0.0:
        Hue_1 = 1 - abs(Hue_1)
        Hue1_2 = 1 - abs(Hue1_2)

    c2.hsv = Hue1_2, sat, val1
    self.temp_colors[2].color = add_alpha(c2)

    c2.hsv = Hue_1, sat, val
    self.temp_colors[3].color = add_alpha(c2)

    shuffle_colors(self.temp_colors)


def update_Complementary(self, c: Color):
    Hue = c.h
    Hue1 = 0.0
    if Hue >= 0.5:
        Hue1 = Hue - 0.5
    else:
        Hue1 = Hue + 0.5
    Saturation = c.s
    if Saturation <= 1.0 and Saturation >= 0.95:
        Saturation = Saturation - 0.1
    if Saturation <= 0.3:
        Saturation = Saturation + 0.25
    Saturation_more = random.uniform(Saturation + 0.05, Saturation + 0.2)
    Saturation_less = random.uniform(Saturation - 0.2, Saturation - 0.05)
    if Saturation_more <= 1.0 and Saturation_more >= 0.95:
        Saturation_more = Saturation_more - 0.1
    if Saturation_more <= 0.6:
        Saturation_more = Saturation_more + 0.45

    if Saturation_less <= 1.0 and Saturation_less >= 0.95:
        Saturation_less = Saturation_less - 0.15

    Value = c.v
    Value_more = random.uniform(Value + 0.05, Value + 0.2)
    Value_less = random.uniform(Value - 0.2, Value - 0.05)
    if Value_more >= 0.0 and Value_more < 0.1:
        Value_more = Value_more + 0.35
    if Value_less >= 0.0 and Value_less < 0.1:
        Value_less = Value_less + 0.3

    c2 = Color()
    c2.hsv = Hue, Saturation_more, Value_less
    self.temp_colors[0].color = add_alpha(c2)

    c2.hsv = Hue, Saturation_less, Value_more
    self.temp_colors[1].color = add_alpha(c2)

    c2.hsv = Hue, Saturation, Value
    self.temp_colors[2].color = add_alpha(c2)

    c2.hsv = Hue1, Saturation_more, Value_less
    self.temp_colors[3].color = add_alpha(c2)

    c2.hsv = Hue1, Saturation, Value
    self.temp_colors[4].color = add_alpha(c2)

    shuffle_colors(self.temp_colors)


def restore(self):
    self.offset_h = 0
    self.offset_s = 0
    self.offset_v = 0

    global history_colors
    history_colors.clear()


def update_generator(self, context):
    restore(self)

    if self.generate_color:
        self.temp_colors.clear()
        for color_item in range(0, 5):
            clr = self.temp_colors.add()
            clr.color = (1, 1, 1, 1)

        c = get_base_color(self)
        if self.method == '0':
            update_Monochromatic(self, c)
        elif self.method == '1':
            update_Analogous(self, c)
        elif self.method == '2':
            update_Complementary(self, c)

    else:
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
    generate_color: BoolProperty(name='Generate', update=update_generator)
    use_custom_color: BoolProperty(default=False, name='Use Custom Color', update=update_generator)
    custom_base_color: FloatVectorProperty(subtype='COLOR', size=4, default=(1, 1, 1, 1), update=update_generator)
    method: EnumProperty(name='Method',
                         items=[
                             ('0', 'Monochromatic', ''),
                             ('1', 'Analogous', ''),
                             ('2', 'Complementary', ''),
                         ], update=update_generator)

    refresh: BoolProperty(name='Refresh', update=update_generator)

    # offset hsv
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
            box.prop(self, 'method')
            row = box.row(align=True)
            row.prop(self, 'use_custom_color')
            if self.use_custom_color:
                row.prop(self, 'custom_base_color', text='')

            box.prop(self, 'refresh', emboss=False, toggle=True)

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
