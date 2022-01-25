import bpy


class CH_OT_paste_color(bpy.types.Operator):
    """Paste hex/rgb string from clipboard with Gamma correct to blender"""
    bl_idname = "ch.color_paster"
    bl_label = "Paste Color"
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return bpy.ops.ui.copy_data_path_button.poll()

    def execute(self, context):
        clipboard = context.window_manager.clipboard
        if not isinstance(clipboard, str): return {'CANCELLED'}
        clipboard.encode('utf8')

        from ..utils.color_correct import Str2Color
        CP = Str2Color(clipboard)
        if not CP.bl_color: return {'CANCELLED'}

        # get property that need to paste
        bpy.ops.ui.copy_data_path_button(full_path=True)
        full_path = context.window_manager.clipboard
        rna, prop = full_path.rsplit('.', 1)
        # some property only accept rgb values
        try:
            try:
                setattr(eval(rna), prop, CP.bl_color)
            except ValueError:
                setattr(eval(rna), prop, CP.bl_color[:3])
        except Exception as e:
            print(f'Paste Color Error:{e}')
        finally:  # restore clip board
            context.window_manager.clipboard = clipboard

        return {'FINISHED'}


def context_menu_func(self, context):
    if CH_OT_paste_color.poll(context):
        layout = self.layout
        layout.separator()
        layout.operator('ch.color_paster', icon='PASTEDOWN')
        layout.separator()


class WM_MT_button_context(bpy.types.Menu):
    bl_label = "WM_MT_button context"

    def draw(self, context):
        pass


def register():
    bpy.utils.register_class(CH_OT_paste_color)

    if not hasattr(bpy.types, 'WM_MT_button_context'):
        bpy.utils.register_class(WM_MT_button_context)
        bpy.types.WM_MT_button_context.append(context_menu_func)


def unregister():
    bpy.utils.unregister_class(CH_OT_paste_color)
    if hasattr(bpy.types, "WM_MT_button_context"):
        bpy.types.WM_MT_button_context.remove(context_menu_func)
