# SPDX-FileCopyrightText: 2026 Atticus
# SPDX-License-Identifier: GPL-3.0-or-later

# Package name can be either "color_helper" for legacy add-on loading or
# "bl_ext.<repository>.color_helper" when installed as a Blender Extension.
__folder_name__ = __package__ or __name__

if "props_palette" in locals():
    import importlib

    importlib.reload(props_palette)
    importlib.reload(op_palette_manage)
    importlib.reload(op_palette_create)
    importlib.reload(op_paste_color)
    importlib.reload(op_palette_color_edit)
    importlib.reload(op_create_nodes_from_palette)
    importlib.reload(op_create_paint_palette)
    importlib.reload(op_palette_export)
    importlib.reload(auto_translation)
    importlib.reload(ui_panel)
    importlib.reload(preferences)
else:
    from .props import palette as props_palette

    from .ops import op_palette_manage
    from .ops import op_palette_create
    from .ops import op_paste_color
    from .ops import op_palette_color_edit
    from .ops import op_create_nodes_from_palette
    from .ops import op_create_paint_palette
    from .ops import op_palette_export_ as op_palette_export

    from .translation import auto_translation
    from .ui import panel as ui_panel
    from . import preferences


modules = (
    props_palette,
    op_palette_manage,
    op_palette_create,
    op_paste_color,
    op_palette_color_edit,
    op_create_nodes_from_palette,
    op_create_paint_palette,
    op_palette_export,
    auto_translation,
    ui_panel,
    preferences,
)


def register():
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()


if __name__ == "__main__":
    register()
