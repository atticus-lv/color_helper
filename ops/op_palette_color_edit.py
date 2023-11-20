import bpy
from bpy.props import IntProperty, BoolProperty, CollectionProperty, FloatVectorProperty, FloatProperty, EnumProperty

from bpy.types import PropertyGroup

import random
from mathutils import Color


class CH_OT_shuffle_palette(bpy.types.Operator):
    """Shuffle Palette Color"""
    bl_idname = "ch.shuffle_palette"
    bl_label = "Shuffle"
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
        elif hue > 1:
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
    elif offset_hue > 1:
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


def update_SplitComplementary(self, c: Color):
    base_hue = c.h
    base_sat = c.s
    base_val = c.v
    offset = self.slider_SplitComplementary_offset

    offset_hue = base_hue + offset
    offset_hue2 = base_hue - offset

    if offset_hue < 0:
        offset_hue = 1 + offset_hue
    elif offset_hue > 1:
        offset_hue = 1 - offset_hue

    if offset_hue2 < 0:
        offset_hue2 = 1 + offset_hue2
    elif offset_hue2 > 1:
        offset_hue2 = 1 - offset_hue2

    offset_val = base_val - 0.3 if base_val < 0.7 else base_val + 0.3
    offset_sat = base_sat - 0.1 if base_sat > 0.2 else base_sat + 0.1
    offset_sat2 = base_sat - 0.05 if base_sat > 0.15 else base_sat + 0.05
    offset_sat3 = base_sat + 0.1 if base_sat > 0.9 else base_sat - 0.1
    offset_sat4 = base_sat + 0.05 if base_sat > 0.95 else base_sat - 0.05

    color_1 = Color()
    color_2 = Color()
    color_3 = Color()
    color_4 = Color()
    color_5 = Color()

    color_1.hsv = offset_hue, max(offset_sat, 0.1), offset_val
    color_2.hsv = offset_hue, offset_sat2, base_val
    color_3.hsv = base_hue, base_sat, base_val
    color_4.hsv = offset_hue2, max(offset_sat3, 0.1), offset_val
    color_5.hsv = offset_hue2, max(offset_sat4, 0.1), base_val

    self.temp_colors[0].color = hsv_2_rgba(color_1)
    self.temp_colors[1].color = hsv_2_rgba(color_2)
    self.temp_colors[2].color = hsv_2_rgba(color_3)
    self.temp_colors[3].color = hsv_2_rgba(color_4)
    self.temp_colors[4].color = hsv_2_rgba(color_5)


def update_Shades(self, c: Color):
    base_hue = c.h
    base_sat = c.s
    base_val = c.v

    offset_val = base_val + 0.3 if base_val < 0.7 else base_val - 0.5
    offset_val2 = base_val + 0.55 if base_val < 0.45 else base_val - 0.25
    offset_val3 = base_val + 0.05 if base_val < 0.95 else base_val - 0.75
    offset_val4 = base_val - 0.1

    color_1 = Color()
    color_2 = Color()
    color_3 = Color()
    color_4 = Color()
    color_5 = Color()

    color_1.hsv = base_hue, base_sat, offset_val
    color_2.hsv = base_hue, base_sat, offset_val2
    color_3.hsv = base_hue, base_sat, base_val
    color_4.hsv = base_hue, base_sat, max(offset_val3, 0.2)
    color_5.hsv = base_hue, base_sat, max(offset_val4, 0.2)

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
        if self.generate_method == '0':
            update_Analogous(self, c)
        elif self.generate_method == '1':
            update_Monochromatic(self, c)
        elif self.generate_method == '2':
            update_Complementary(self, c)
        elif self.generate_method == '3':
            update_SplitComplementary(self, c)
        elif self.generate_method == '4':
            update_Shades(self, c)

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

GENERATE_RULES = [
    ('0', 'Analogous', ''),
    ('1', 'Monochromatic', ''),
    ('2', 'Complementary', ''),
    ('3', 'Split Complementary', ''),
    ('4', 'Shades', ''),
    ('5', 'Random', ''),  # remove later
]


class CH_OT_edit_color(bpy.types.Operator):
    """Create, Offset, Sort Palette Colors"""
    bl_idname = 'ch.edit_color'
    bl_label = 'Edit Color'
    bl_options = {"INTERNAL", "UNDO"}

    temp_colors: CollectionProperty(type=TempColorProps)
    src_palette = None
    palette_index: IntProperty()

    # color generate
    #################
    generate_color: BoolProperty(name='Generate', update=update_generator)
    generate_method: EnumProperty(name='Method',
                                  items=GENERATE_RULES[:-1], update=update_generator)

    base_color: FloatVectorProperty(subtype='COLOR', size=4, min=0, max=1, default=(0.48, 0.6, 0, 1),
                                    update=update_generator)

    refresh: BoolProperty(name='Refresh', update=refresh_base_color)

    # Analogous
    slider_Analogous_offset: FloatProperty(name='Offset', min=0, max=0.2, default=0.1,
                                           update=update_generator)  # 5 color 4 step
    # Split Complementary
    slider_SplitComplementary_offset: FloatProperty(name='Offset', min=0, max=0.5, default=0.25,
                                                    update=update_generator)  # 2 step

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

        if self.generate_color:
            update_generator(self, context)

        return context.window_manager.invoke_props_dialog(self, width=int(context.region.width / 2))

    def apply_color(self):
        collection = bpy.context.scene.ch_palette_collection[bpy.context.scene.ch_palette_collection_index]
        self.src_palette = collection.palettes[self.palette_index]

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
            if self.generate_method == '0':
                box.prop(self, 'slider_Analogous_offset', slider=True)
            elif self.generate_method == '3':
                box.prop(self, 'slider_SplitComplementary_offset', slider=True)

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

        return {'FINISHED'}


class CH_OT_batch_generate_color(bpy.types.Operator):
    """Batch Create Color palettes"""
    bl_idname = 'ch.batch_generate_color'
    bl_label = 'Generate'
    bl_options = {"REGISTER", "UNDO_GROUPED"}

    count: IntProperty(name='Count', min=1, soft_max=10, max=100, default=5)
    generate_method: EnumProperty(name='Method',
                                  items=GENERATE_RULES)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, )

    def execute(self, context):
        if len(context.scene.ch_palette_collection) == 0:
            collection = context.scene.ch_palette_collection.add()
            collection.name = 'Collection'
        else:
            collection = context.scene.ch_palette_collection[context.scene.ch_palette_collection_index]

        for i in range(0, self.count):
            bpy.ops.ch.add_palette()

            src_palette = collection.palettes[-1]
            src_palette.hide = True

            bpy.ops.ch.edit_color(
                generate_color=True,
                generate_method=str(round(random.uniform(0, 4))) if
                self.generate_method == '5' else self.generate_method,
                base_color=(random.random(), random.random(), random.random(), 1),
                palette_index=-1,
            )

        return {"FINISHED"}


pantone_names = []


class CH_OT_copy_pantone_names(bpy.types.Operator):
    bl_idname = 'ch.copy_pantone_names'
    bl_label = 'Copy'

    def execute(self, context):
        global pantone_names
        s = ''
        for name in pantone_names:
            s += 'Pantone ' + name + '  ' if name.isdigit() else name + '  '

        bpy.context.window_manager.clipboard = s

        return {"FINISHED"}


def refresh_pantone(self, context):
    global pantone_names
    pantone_names.clear()

    from ..utils.color_correct import find_closest_pantone

    for color_item in self.temp_colors:
        name, color = find_closest_pantone(color_item.color[0:3], white_point=self.white_point)
        rgb = list(color)
        rgb.append(1)

        pantone_names.append(name)
        color_item.color = rgb


class CH_OT_convert_pantone_color(bpy.types.Operator):
    bl_idname = 'ch.convert_pantone_color'
    bl_label = 'Convert to Pantone Color'
    bl_options = {"REGISTER", "UNDO"}

    temp_colors: CollectionProperty(type=TempColorProps)
    src_palette = None
    palette_index: IntProperty()

    white_point: EnumProperty(name='White Point', items=[
        ('D50', 'D50', ''),
        ('D55', 'D55', ''),
        ('D65', 'D65', ''),
    ], default='D55', update=refresh_pantone)

    @classmethod
    def poll(cls, context):
        return (
                (context.area.ui_type == 'VIEW_3D') or
                (hasattr(context.space_data, 'edit_tree') and
                 context.space_data.edit_tree and
                 context.space_data.edit_tree.bl_idname == 'ShaderNodeTree')
        )

    def invoke(self, context, event):
        self.temp_colors.clear()
        global pantone_names
        pantone_names.clear()

        collection = context.scene.ch_palette_collection[context.scene.ch_palette_collection_index]
        self.src_palette = collection.palettes[self.palette_index]

        for color_item in self.src_palette.colors:
            clr = self.temp_colors.add()
            clr.color = color_item.color

        refresh_pantone(self, context)

        return context.window_manager.invoke_props_dialog(self, width=int(context.region.width / 2))

    def draw(self, context):
        global pantone_names

        collection = context.scene.ch_palette_collection[context.scene.ch_palette_collection_index]
        self.src_palette = collection.palettes[self.palette_index]

        layout = self.layout

        box = layout.box()
        box.prop(self, 'white_point')

        col = layout.column(align=True)

        row = col.row(align=True)
        row.scale_y = 1.5

        row.label(text='Origin')
        for i, color_item in enumerate(self.src_palette.colors):
            row.prop(color_item, 'color')

        row = col.row(align=True)
        row.scale_y = 2

        row.label(text='Pantone')
        for i, color_item in enumerate(self.temp_colors):
            row.prop(color_item, 'color')

        row = layout.row(align=True)
        row.label(text='Name')
        for name in pantone_names:
            row.label(text=name)

        layout.operator('ch.copy_pantone_names', text='Copy Names', icon='PASTEFLIPUP')

    def execute(self, context):
        refresh_pantone(self, context)
        for i, color_item in enumerate(self.src_palette.colors):
            color_item.color = self.temp_colors[i].color

        return {"FINISHED"}






def register():
    bpy.utils.register_class(CH_OT_shuffle_palette)
    bpy.utils.register_class(TempColorProps)
    bpy.utils.register_class(CH_OT_edit_color)
    bpy.utils.register_class(CH_OT_batch_generate_color)
    bpy.utils.register_class(CH_OT_convert_pantone_color)
    bpy.utils.register_class(CH_OT_copy_pantone_names)


def unregister():
    bpy.utils.unregister_class(CH_OT_shuffle_palette)
    bpy.utils.unregister_class(TempColorProps)
    bpy.utils.unregister_class(CH_OT_edit_color)
    bpy.utils.unregister_class(CH_OT_batch_generate_color)
    bpy.utils.unregister_class(CH_OT_convert_pantone_color)
    bpy.utils.unregister_class(CH_OT_copy_pantone_names)
