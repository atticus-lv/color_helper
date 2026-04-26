# SPDX-FileCopyrightText: 2026 Atticus
# SPDX-License-Identifier: GPL-3.0-or-later

import importlib
import os
import sys

# Package name can be either "color_helper" for legacy add-on loading or
# "bl_ext.<repository>.color_helper" when installed as a Blender Extension.
__folder_name__ = __package__ or __name__
__dict__ = {}

addon_dir = os.path.dirname(__file__)

# get all .py file dir
py_paths = [
    os.path.join(root, f)
    for root, dirs, files in os.walk(addon_dir)
    for f in files
    if f.endswith('.py') and f != '__init__.py'
]

for path in py_paths:
    name = os.path.basename(path)[:-3]
    module_parts = os.path.splitext(os.path.relpath(path, addon_dir))[0].split(os.sep)

    if 'colorthief' not in module_parts:
        __dict__[name] = __folder_name__ + '.' + '.'.join(module_parts)

# auto reload
for name in __dict__.values():
    if name in sys.modules:
        importlib.reload(sys.modules[name])
    else:
        globals()[name] = importlib.import_module(name)
        setattr(globals()[name], 'modules', __dict__)


def register():
    for name in __dict__.values():
        if name in sys.modules and hasattr(sys.modules[name], 'register'):
            try:
                sys.modules[name].register()
            except ValueError:  # open template file may cause this problem
                pass


def unregister():
    for name in __dict__.values():
        if name in sys.modules and hasattr(sys.modules[name], 'unregister'):
            try:
                sys.modules[name].unregister()
            except Exception:
                pass


if __name__ == '__main__':
    register()
