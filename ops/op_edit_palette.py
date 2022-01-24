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


def redraw_area():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw()


class CH_OT_add_collection(bpy.types.Operator):
    bl_idname = 'ch.add_collection'
    bl_label = 'Add Collection'

    def execute(self, context):
        collection = context.scene.ch_palette_collection.add()
        collection.name = 'Collection' + str(len(context.scene.ch_palette_collection))
        context.scene.ch_palette_enum_collection = str(len(context.scene.ch_palette_collection) - 1)

        redraw_area()

        return {'FINISHED'}


class CH_OT_remove_collection(bpy.types.Operator):
    bl_idname = 'ch.remove_collection'
    bl_label = 'Remove Collection'

    collection_index: IntProperty()

    # def invoke(self, context, event):
    #     return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        context.scene.ch_palette_collection.remove(self.collection_index)
        context.scene.ch_palette_enum_collection = '0' if self.collection_index - 1 <= 0 else f'{self.collection_index - 1}'

        redraw_area()

        return {'FINISHED'}


class CH_OT_remove_palette(bpy.types.Operator):
    bl_idname = 'ch.remove_palette'
    bl_label = 'Remove Palette'

    palette_index: IntProperty()

    def execute(self, context):
        collection = context.scene.ch_palette_collection[context.scene.ch_palette_collection_index]
        collection.palettes.remove(self.palette_index)

        redraw_area()

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
        clr = item.colors.add()
        clr.color = (0.8, 0.8, 0.8, 1)
        redraw_area()

        return {'FINISHED'}


class CH_OT_copy_palette(bpy.types.Operator):
    bl_idname = 'ch.copy_palette'
    bl_label = 'Copy'

    palette_index: IntProperty()

    def execute(self, context):
        collection = context.scene.ch_palette_collection[context.scene.ch_palette_collection_index]
        src_item = collection.palettes[self.palette_index]

        item = collection.palettes.add()

        item.name = src_item.name + '_copy'

        for color_item in src_item.colors:
            clr = item.colors.add()
            clr.color = color_item.color

        redraw_area()

        return {'FINISHED'}


class CH_PT_move_palette(bpy.types.Operator):
    bl_idname = 'ch.move_palette'
    bl_label = 'Move to Collection'

    palette_index: IntProperty()

    dep_classes = []

    def execute(self, context):
        self.dep_classes.clear()
        active_coll = context.scene.ch_palette_collection[context.scene.ch_palette_collection_index]
        active_index = self.palette_index
        src_palette = active_coll.palettes[active_index]

        for index, coll in enumerate(context.scene.ch_palette_collection):
            if index == context.scene.ch_palette_collection_index: continue

            # only for register
            def execute(self, context):
                palette_item = self.target_collection.palettes.add()
                palette_item.name = src_palette.name
                for color_item in self.src_palette.colors:
                    clr = palette_item.colors.add()
                    clr.color = color_item.color

                active_coll.palettes.remove(active_index)

                return {'FINISHED'}

            op_cls = type("DynOp",
                          (bpy.types.Operator,),
                          {"bl_idname": f'ch.move_to_collection{index}',
                           "bl_label": coll.name,
                           "bl_description": f"Move Palette to {coll.name}",
                           "execute": execute,
                           # custom pass in
                           'target_collection': coll,
                           'src_palette': src_palette,
                           },
                          )

            self.dep_classes.append(op_cls)

        # register
        for cls in self.dep_classes:
            bpy.utils.register_class(cls)

        dep_classes = self.dep_classes

        def draw_all_coll(self, context):
            layout = self.layout
            for cls in dep_classes:
                layout.operator(cls.bl_idname, icon='COLOR')

        context.window_manager.popup_menu(draw_all_coll, title="Move To Collection")

        redraw_area()

        return {'FINISHED'}


class CH_OT_add_color(bpy.types.Operator):
    bl_idname = 'ch.add_color'
    bl_label = 'Add Color'

    palette_index: IntProperty()
    color_index: IntProperty()

    def execute(self, context):
        collection = context.scene.ch_palette_collection[context.scene.ch_palette_collection_index]
        palette = collection.palettes[self.palette_index]

        item = palette.colors.add()
        item.color = (0.8, 0.8, 0.8, 1)

        redraw_area()

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

        redraw_area()

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
                [(r, g, b)[int(self.mode)] for (r, g, b) in [rgb_to_hsv(*color.color[:3])]],  # sort key
                tuple(color.color)  # source color
            ) for color in palette.colors], reverse=self.reverse
        )

        for new_index, (hsv, color) in enumerate(original_colors):
            palette.colors[new_index].color = color

        redraw_area()

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'mode', expand=True)
        layout.prop(self, 'reverse')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=200)


classes = (
    CH_OT_add_collection,
    CH_OT_remove_collection,

    CH_OT_add_palette,
    CH_OT_remove_palette,

    CH_OT_copy_palette,
    CH_PT_move_palette,

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
