import bpy
from bpy.props import *


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
        if len(context.scene.ch_palette_collection) != 0:
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
    bl_label = 'Palette'

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


class CH_PT_move_palette():
    palette_index: IntProperty()
    action = None

    def execute(self, context):
        active_coll = context.scene.ch_palette_collection[context.scene.ch_palette_collection_index]
        active_index = self.palette_index

        my_list = active_coll.palettes
        index = active_index
        neighbor = index + (-1 if self.action == 'UP' else 1)
        my_list.move(neighbor, index)

        redraw_area()
        return {'FINISHED'}


class CH_PT_move_palette_up(CH_PT_move_palette, bpy.types.Operator):
    bl_idname = 'ch.move_palette_up'
    bl_label = 'Move Up'

    action = 'UP'


class CH_PT_move_palette_down(CH_PT_move_palette, bpy.types.Operator):
    bl_idname = 'ch.move_palette_down'
    bl_label = 'Move Down'

    action = 'DOWN'


class CH_PT_sort_palette(bpy.types.Operator):
    bl_idname = 'ch.sort_palette'
    bl_label = 'Sort Palette'

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        active_coll = context.scene.ch_palette_collection[context.scene.ch_palette_collection_index]
        active_index = self.palette_index

        my_list = active_coll.palettes
        index = active_index
        neighbor = index + (-1 if self.action == 'UP' else 1)
        my_list.move(neighbor, index)

        redraw_area()
        return {'FINISHED'}


class CH_PT_move_palette_to_collection(bpy.types.Operator):
    bl_idname = 'ch.move_palette_to_collection'
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
    """Shift: Paste from Clipboard (Hex/rgb string with gamma convert)"""
    bl_idname = 'ch.add_color'
    bl_label = 'Add Color'

    palette_index: IntProperty()
    color_index: IntProperty()

    def invoke(self, context, event):
        if event.shift:
            self.add_from_clipboard()
            return {"FINISHED"}
        else:
            return self.execute(context)

    def add_from_clipboard(self):
        bpy.ops.ch.paste_and_add_color(palette_index=self.palette_index)

    def execute(self, context):
        collection = context.scene.ch_palette_collection[context.scene.ch_palette_collection_index]
        palette = collection.palettes[self.palette_index]

        if len(palette.colors) == 0:
            new_clr = (0.8, 0.8, 0.8, 1)
        else:
            pre_clr = palette.colors[-1].color
            new_clr = (pre_clr[0] - 0.2 if pre_clr[0] >= 0.2 else 0,
                       pre_clr[1] - 0.2 if pre_clr[1] >= 0.2 else 0,
                       pre_clr[2] - 0.2 if pre_clr[2] >= 0.2 else 0,
                       pre_clr[3])

        item = palette.colors.add()
        item.color = new_clr

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


classes = (
    CH_OT_add_collection,
    CH_OT_remove_collection,

    CH_OT_add_palette,
    CH_OT_remove_palette,
    CH_PT_move_palette_up,
    CH_PT_move_palette_down,

    CH_OT_copy_palette,
    CH_PT_move_palette_to_collection,

    CH_OT_add_color,
    CH_OT_remove_color
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
