import bpy
from bpy.props import *
from bpy.types import PropertyGroup


def update_color(self, context):
    path = self.color.path_from_id().split('.colors')[0]
    palette = eval('bpy.context.scene' + '.' + path)
    index = int(palette.path_from_id().split('.palettes')[-1][1:-1])
    if palette.node_group and palette.node_group_update:
        bpy.ops.ch.create_nodes_from_palette('INVOKE_DEFAULT', palette_index=index)


class PaletteColorProps(PropertyGroup):
    color: FloatVectorProperty(
        subtype='COLOR', name='', min=0.0, max=1.0, size=4, update=update_color)


def poll_shader_tree(self, object):
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
    node_group: PointerProperty(name='Node Group', type=bpy.types.NodeTree, poll=poll_shader_tree)
    node_group_update: BoolProperty('Update Node Group', default=False)
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


def enum_collection_callback(self, context):
    return [(f'{i}', collection.name, '') for i, collection in enumerate(context.scene.ch_palette_collection)]


def update_enum_collection(self, context):
    setattr(context.scene, 'ch_palette_collection_index', int(context.scene.ch_palette_enum_collection))


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.ch_palette_collection = CollectionProperty(type=PaletteCollectionProps)
    bpy.types.Scene.ch_palette_collection_index = IntProperty()
    # UI
    bpy.types.Scene.ch_palette_enum_collection = EnumProperty(name='Color Collection',
                                                              items=enum_collection_callback,
                                                              update=update_enum_collection)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.ch_palette_collection
    del bpy.types.Scene.ch_palette_collection_index
