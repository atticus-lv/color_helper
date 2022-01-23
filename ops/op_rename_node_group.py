import bpy
from bpy.props import IntProperty, StringProperty


class CH_OT_rename_node_group(bpy.types.Operator):
    """Rename Node group that has the same name as this palette\nSo palette's name update will not bind to that group"""
    bl_idname = 'ch.rename_node_group'
    bl_label = 'Rename Node Group'
    bl_options = {"REGISTER", "UNDO"}

    palette_index: IntProperty(options={'HIDDEN'})

    node_group: StringProperty(name='New Name')

    nt = None

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'node_group')

    def execute(self, context):
        self.nt.name = self.node_group
        return {'FINISHED'}

    def invoke(self, context, event):
        collection = context.scene.ch_palette_collection[context.scene.ch_palette_collection_index]
        palette = collection.palettes[self.palette_index]

        if palette.name not in bpy.data.node_groups:
            self.report({"ERROR"}, f'No Shader node group call "{palette.name}"')
            return {'FINISHED'}

        self.node_group = palette.name
        self.nt = bpy.data.node_groups.get(self.node_group)

        return context.window_manager.invoke_props_dialog(self)


def register():
    bpy.utils.register_class(CH_OT_rename_node_group)


def unregister():
    bpy.utils.unregister_class(CH_OT_rename_node_group)
