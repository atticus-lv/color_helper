import requests
import json
import random
import math

import bpy
from bpy.props import IntProperty, StringProperty, BoolProperty, FloatVectorProperty, CollectionProperty, EnumProperty

URL = 'http://colormind.io/api/'
MODELS = {
    'models': []
}

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
}


def srgb_2_linear(c, gamma=2.4):
    if c < 0:
        return 0
    elif c < 0.04045:
        return c / 12.92
    else:
        return ((c + 0.055) / 1.055) ** gamma


def linear_2_srgb(c, gamma_value=2.4):
    if c < 0.0031308:
        srgb = 0.0 if c < 0.0 else c * 12.92
    else:
        srgb = 1.055 * math.pow(c, 1.0 / gamma_value) - 0.055

    return srgb


def rgb255_2_rgb1(col):
    return [rgb / 256 for rgb in col]


def rgb1_2rgb_255(col):
    return [int(c * 256) for c in col]


def parse_content(b: bytes):
    print(b.decode('utf-8'))
    return json.loads(b.decode('utf-8'))


def get_color_models() -> list[str] | None:
    # {"result":["default","ui","makoto_shinkai","metroid_fusion","akira_film","flower_photography"]}
    response = requests.get('http://colormind.io/list/')
    if response.status_code == 200:
        res = parse_content(response.content)
        print(res)
        return res['result']


def gen_random_colors(model='default'):
    data = f'{{"model":"{model}"}}'

    response = requests.post(URL, headers=headers, data=data)
    if response.status_code == 200:
        res = parse_content(response.content)
        return res['result']


def gen_palette_from_colors(colors, model='default'):
    fix_colors = []
    for col in colors:
        fix_colors.append(rgb1_2rgb_255(col)[:3])

    n_to_add = 5 - len(fix_colors)

    for i in range(n_to_add):
        fix_colors.append("N")

    str_json = f'{fix_colors}'.replace("'", '"')

    data = f'{{"input":{str_json},"model":"{model}"}}'
    print('DATA: ', data)

    response = requests.post('http://colormind.io/api/', headers=headers, data=data)

    if response.status_code == 200:
        res = parse_content(response.content)
        return res['result']


def get_ai_color(self, context):
    if self.generate is True:

        colors_to_input = [getattr(self, f'col{i + 1}') for i in range(4) if getattr(self, f'use_col{i + 1}')]

        if len(colors_to_input) > 0:
            colors = gen_palette_from_colors(colors_to_input)
        else:
            colors = gen_random_colors()

        print('Get AI colors: ', colors)

        if colors:
            fix_colors = [rgb255_2_rgb1(c) + [1] for c in colors]

            self.temp_colors[0].color = fix_colors[0]
            self.temp_colors[1].color = fix_colors[1]
            self.temp_colors[2].color = fix_colors[2]
            self.temp_colors[3].color = fix_colors[3]
            self.temp_colors[4].color = fix_colors[4]
        else:
            self.report({'ERROR'}, 'Connect Failed')

        self.generate = False


class TempColorProps(bpy.types.PropertyGroup):
    color: FloatVectorProperty(
        subtype='COLOR', name='', min=0, soft_max=1, size=4)


class CH_OT_palette_from_ai(bpy.types.Operator):
    bl_idname = 'ch.palette_from_ai'
    bl_label = 'Palette from AI'
    bl_options = {"REGISTER", "UNDO"}

    _enum_model = []

    def enum_models(self, context):
        enum_items = CH_OT_palette_from_ai._enum_model
        enum_items.clear()

        if len(MODELS['models']) == 0:
            MODELS['models'] = get_color_models()

        enum_items = [(m, m, '') for m in MODELS['models']]
        return enum_items

    # model: EnumProperty(
    #     name="Model",
    #     items=enum_models,
    # )

    use_col1: BoolProperty(name='Color 1', default=True)
    use_col2: BoolProperty(name='Color 2', default=True)
    use_col3: BoolProperty(name='Color 3', default=False)
    use_col4: BoolProperty(name='Color 4', default=False)

    col1: FloatVectorProperty(name='Color 1', subtype='COLOR', size=4, default=(1, 1, 1, 1))
    col2: FloatVectorProperty(name='Color 2', subtype='COLOR', size=4, default=(1, 1, 1, 1))
    col3: FloatVectorProperty(name='Color 3', subtype='COLOR', size=4, default=(1, 1, 1, 1))
    col4: FloatVectorProperty(name='Color 4', subtype='COLOR', size=4, default=(1, 1, 1, 1))

    temp_colors: CollectionProperty(type=TempColorProps)

    generate: BoolProperty(default=False, name='Generate', options={'SKIP_SAVE'}, update=get_ai_color)

    def invoke(self, context, event):
        self.temp_colors.clear()
        for i in range(5):
            clr = self.temp_colors.add()
            clr.color = (0, 0, 0, 1)

        for i in range(4):
            setattr(self, f'col{i}', (random.random(), random.random(), random.random(), 1))

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        # layout.prop(self, 'model')

        row = layout.row(align=True)
        row.scale_y = 1.5
        for color_item in self.temp_colors:
            row.prop(color_item, 'color')

        for i in range(4):
            row = layout.row(align=True)
            row.prop(self, f'use_col{i + 1}')
            if getattr(self, f'use_col{i + 1}'):
                row.prop(self, f'col{i + 1}', text='')

        layout.prop(self, 'generate', toggle=True, icon='FILE_REFRESH')

    def execute(self, context):
        return {"FINISHED"}


register, unregister = bpy.utils.register_classes_factory([TempColorProps, CH_OT_palette_from_ai])
