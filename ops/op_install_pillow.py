import bpy
import subprocess
import sys
import site
import importlib
from pathlib import Path


USER_SITE = site.getusersitepackages()

if USER_SITE not in sys.path:
    sys.path.append(USER_SITE)

Image = None


def _import_pillow():
    '''Import Pillow and test which formats are supported.'''
    global Image

    try:
        from PIL import Image
    except ImportError:
        pass

_import_pillow()

def support_pillow() -> bool:
    '''Check whether Pillow is installed.'''
    if not Image and 'PIL' in sys.modules:
        _import_pillow()

    return bool(Image)

def install_pillow() -> bool:
    '''Install Pillow and import the Image module.'''
    if 'python' in Path(sys.executable).stem.lower():
        exe = sys.executable
    else:
        exe = bpy.app.binary_path_python

    args = [exe, '-m', 'ensurepip', '--user', '--upgrade', '--default-pip']
    if subprocess.call(args=args, timeout=600):
        return False

    args = [exe, '-m', 'pip', 'install', '--user', '--upgrade', 'Pillow']
    if subprocess.call(args=args, timeout=600):
        return False

    name = 'PIL'
    path = Path(USER_SITE).joinpath(name, '__init__.py')

    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)

    sys.modules[module.__name__] = module
    spec.loader.exec_module(module)

    return support_pillow()

class CH_OT_install_pillow(bpy.types.Operator):
    '''Base class for an operator that installs Pillow.
    Usage:
    -   Inherit bpy.types.Operator and InstallPillow.
    -   Make sure to set bl_idname, it must be unique.
    '''
    bl_label = 'Install Pillow'
    bl_idname = 'ch.install_pillow'
    bl_description = '.\n'.join((
        'Install the Python Imaging Library',
        'This could take a few minutes',
    ))
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self: bpy.types.Operator, context: bpy.types.Context) -> set:
        if install_pillow():
            self.report({'INFO'}, 'Successfully installed Pillow')
        else:
            self.report({'WARNING'}, 'Failed to install Pillow')

        return {'FINISHED'}

def register():
    bpy.utils.register_class(CH_OT_install_pillow)

def unregister():
    bpy.utils.unregister_class(CH_OT_install_pillow)