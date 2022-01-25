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
