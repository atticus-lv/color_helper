# gamma correct
######################
def srgb_2_linear(c, gamma=2.4):
    if c < 0:
        return 0
    elif c < 0.04045:
        return c / 12.92
    else:
        return ((c + 0.055) / 1.055) ** gamma


from math import pow


def linear_2_srgb(c, gamma_value=2.4):
    if c < 0.0031308:
        srgb = 0.0 if c < 0.0 else c * 12.92
    else:
        srgb = 1.055 * pow(c, 1.0 / gamma_value) - 0.055

    return srgb


######################

# Text convert (Include gamma correct)
######################
def hex_to_rgba(hex_str, alpha=1):
    if hex_str.startswith('#'): hex_str = hex_str[1:]

    hex = eval(f'0x{hex_str}')
    r = (hex & 0xff0000) >> 16
    g = (hex & 0x00ff00) >> 8
    b = (hex & 0x0000ff)

    return tuple([srgb_2_linear(c / 0xff) for c in (r, g, b)] + [alpha])


def rgb_str_to_rgba(rgb_str, alpha=1, has_prefix=True):
    rgb = [c / 255 for c in eval(rgb_str[3:] if has_prefix else rgb_str)]
    rgb = [srgb_2_linear(c) for c in rgb]

    if len(rgb) == 3: rgb.append(alpha)
    return rgb


######################
# String Convert
######################
import re

rules = {
    'HEX': r'^#?[a-fA-F\d]{6}$',
    'RGB': r'^[rR][gG][Bb][Aa]?[\(]([\s]*(2[0-4][0-9]|25[0-5]|[01]?[0-9][0-9]?),){2}[\s]*(2[0-4][0-9]|25[0-5]|[01]?[0-9][0-9]?),?[\s]*(0\.\d{1,2}|1|0)?[\)]{1}$',
    # 'HSL': r'^[Hh][Ss][Ll][\(](((([\d]{1,3}|[\d\%]{2,4})[\,]{0,1})[\s]*){3})[\)]',
    'RGB_pure': r'^([\s]*(2[0-4][0-9]|25[0-5]|[01]?[0-9][0-9]?),){2}[\s]*(2[0-4][0-9]|25[0-5]|[01]?[0-9][0-9]?),?[\s]*(0\.\d{1,2}|1|0)?$',
    # 'HSV':'[Hh][Ss][Vv][\(](((([\d]{1,3}|[\d\%]{2,4})[\,]{0,1})[\s]*){3})[\)]'
}


class Str2Color():
    def __init__(self, string):
        self.string = string

    @property
    def bl_color(self):
        ans = self.match_rule()
        if not ans: return

        rule, string = ans

        if rule == 'HEX':
            return hex_to_rgba(string)
        elif rule in {'RGB', 'RGB_pure'}:
            return rgb_str_to_rgba(string, has_prefix=True if rule == 'RGB' else False)
        # elif rule == 'HSL':
        #     return self.HSL_to_RGB(string)

    def match_rule(self):
        for k, v in rules.items():
            m_obj = re.match(v, self.string)
            if m_obj: return k, m_obj.group(0)


######################
# Lab Convert
######################

white_points = {
    'D50': [0.9642, 1.0000, 0.8251],
    'D55': [0.9568, 1.0000, 0.9214],
    'D65': [0.9504, 1.0000, 1.0888],

}


def rgb2lab(inputColor, srgb=False, white_point='D55'):
    if srgb is True:
        RGB = srgb_2_linear(inputColor)
    else:
        RGB = inputColor

    XYZ = [0, 0, 0, ]

    X = RGB[0] * 0.4124 + RGB[1] * 0.3576 + RGB[2] * 0.1805
    Y = RGB[0] * 0.2126 + RGB[1] * 0.7152 + RGB[2] * 0.0722
    Z = RGB[0] * 0.0193 + RGB[1] * 0.1192 + RGB[2] * 0.9505

    XYZ[0] = round(X, 4)
    XYZ[1] = round(Y, 4)
    XYZ[2] = round(Z, 4)

    wp_xyz = white_points[white_point]

    XYZ[0] = float(XYZ[0]) / wp_xyz[0] * 100
    XYZ[1] = float(XYZ[1]) / wp_xyz[1] * 100
    XYZ[2] = float(XYZ[2]) / wp_xyz[2] * 100

    for i, value in enumerate(XYZ):
        if value > 0.008856:
            value = value ** (1 / 3)
        else:
            value = (7.787 * value) + (16 / 116)

        XYZ[i] = value

    Lab = [0, 0, 0]

    L = (116 * XYZ[1]) - 16
    a = 500 * (XYZ[0] - XYZ[1])
    b = 200 * (XYZ[1] - XYZ[2])

    Lab[0] = round(L, 4)
    Lab[1] = round(a, 4)
    Lab[2] = round(b, 4)

    return Lab


import numpy as np


def find_closest_lab_color(colors_list, color):
    colors = np.array(colors_list)
    color = np.array(color)
    distances = np.sqrt(np.sum((colors_list - color) ** 2, axis=1))
    index_of_smallest = np.where(distances == np.amin(distances))
    smallest_distance = colors[index_of_smallest]
    return index_of_smallest, smallest_distance[0]


import os


def find_closest_pantone(rgb, white_point='D55'):
    import json
    dict_file = os.path.join(os.path.dirname(__file__), 'lib', 'pantone_hex.json')
    with open(dict_file) as f:
        pantone_dict = json.load(f)

    pantone_names = list(pantone_dict.keys())
    pantone_hex = list(pantone_dict.values())
    pantone_rgb = [hex_to_rgba(value)[0:3] for value in pantone_hex]
    pantone_lab = [rgb2lab(value, white_point='D55') for value in pantone_rgb]

    idx, lab_color = find_closest_lab_color(pantone_lab, rgb2lab(rgb, white_point='D55'))
    idx = idx[0][0]

    return (pantone_names[idx], pantone_rgb[idx])
