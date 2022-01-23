import bpy
from bpy.props import *
from bpy.types import PropertyGroup


class PaletteColorProps(PropertyGroup):
    color: FloatVectorProperty(
        subtype='COLOR', name='', min=0.0, max=1.0, size=4)

def poll_shader_tree(self,object):
    return object.bl_idname == 'ShaderNodeTree'

class PaletteProps(PropertyGroup):
    # def get_name(self):
    #     return self.get("name",'Palette')
    #
    # def set_name(self, value):
    #     old_name = self.get("name",'Palette')
    #
    #     if old_name in bpy.data.node_groups:
    #         nt = bpy.data.node_groups.get(old_name)
    #         nt.name = value
    #     self["name"] = value

    # name: StringProperty(name='Name', get=get_name, set=set_name)
    name: StringProperty(name='Name')
    colors: CollectionProperty(type=PaletteColorProps)
    # bind

    node_group:PointerProperty(type = bpy.types.NodeTree,poll = poll_shader_tree)

    # UI
    edit_mode: BoolProperty(name='Edit', default=False)


class PaletteCollectionProps(PropertyGroup):
    name: StringProperty(name='Name')
    palettes: CollectionProperty(type=PaletteProps)

    library: StringProperty(name='Library', subtype='DIR_PATH')


classes = (
    PaletteColorProps,
    PaletteProps,
    PaletteCollectionProps
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.ch_palette_collection = CollectionProperty(type=PaletteCollectionProps)
    bpy.types.Scene.ch_palette_collection_index = IntProperty()


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.ch_palette_collection
    del bpy.types.Scene.ch_palette_collection_index
