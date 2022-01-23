import math
from ..ops.op_export_palette import COLOR_WIDTH, COLOR_HEIGHT


def gamma_correct(c, gamma=2.4):
    if c < 0:
        return 0
    elif c < 0.04045:
        return c / 12.92
    else:
        return ((c + 0.055) / 1.055) ** gamma


def gamma_invert(c, gamma_value=2.4):
    if c < 0.0031308:
        srgb = 0.0 if c < 0.0 else c * 12.92
    else:
        srgb = 1.055 * math.pow(c, 1.0 / gamma_value) - 0.055

    return srgb


def round_color_tuple(color_tuple, precision=4):
    return tuple((round(cv, precision) for cv in color_tuple))


def is_color_similar(color1, color2, max_diff=0.05):
    """
    Return as early as possible, False whenever rgb values (color[0], color[1] or color[2])
    of the two colors differ more then the max.
    """
    for i in range(3):
        if abs(color1[i] - color2[i]) > max_diff:
            return False

    return True


def get_distinct_colors(color_tuples, maximum_colors, max_color_diff=0.05):
    distinct_colors = []

    for _count, color in color_tuples:
        new_color = True
        for dist_color in distinct_colors:
            if is_color_similar(dist_color, color, max_diff=max_color_diff):
                new_color = False
                break

        if new_color:
            distinct_colors.append(color)

        if len(distinct_colors) == maximum_colors:
            break

    return distinct_colors


def extract_from_palette(image):
    channel_count = image.channels
    pixels = image.pixels[:]  # this takes 99% of the time

    start_pixel = int(COLOR_WIDTH / 2)
    len_colors = image.size[0] // COLOR_WIDTH

    def get_color(x):
        start_index = x * channel_count
        return round_color_tuple(pixels[start_index:start_index + channel_count])

    colors = [get_color(x=start_pixel + i * COLOR_WIDTH) for i in range(len_colors)]
    colors[:] = [[gamma_correct(c) for c in color] for color in colors]

    return colors


def extract_from_image(image):
    """
    Use the user preferences to determine colors
    """
    max_colors_to_return = 5
    determine_distinct_colors = 0.05
    pixel_threshold = 800
    ignore_alpha_below = 1
    analyse_all_pixels = False
    ###########

    new_colors = {}
    for new_color in PixelIterator(image=image, analyse_all_pixels=analyse_all_pixels):
        if new_color[3] >= ignore_alpha_below:
            new_colors.setdefault(new_color, 0)
            new_colors[new_color] += 1

    color_tuples = sorted([(count, color) for color, count in new_colors.items()], reverse=True)
    if pixel_threshold > 0.0:
        highest_frequency = color_tuples[0][0]
        threshold = int(highest_frequency / pixel_threshold)
        color_tuples = [(count, color) for count, color in color_tuples if count > threshold]

    colors = []

    if determine_distinct_colors > 0:
        colors = get_distinct_colors(color_tuples, max_colors_to_return, determine_distinct_colors)
    else:
        colors = [color for _, color in color_tuples]

    return colors[:max_colors_to_return]


class PixelIterator:
    """
    Iterate over blender Image pixel data.
    For small images, loop over every single pixel.
    For images larger than 1000 pixels, only consider 33 x 33 = 999 pixels.
    These 999 pixels are chosen from an 'equally distributed grid'.

    Return the color values as a Color tuple of floats.
    The color tuple always contains 4 rounded values (including the gamma value that will be 1 by default).
    """

    def __init__(self, image, analyse_all_pixels=False):
        self.analyse_all_pixels = analyse_all_pixels
        self.channel_count = image.channels
        self.width, self.height = image.size
        self.pixels = image.pixels[:]  # way faster to use a Python list, instead of the Blender pixel datatype

        assert self.channel_count in [3, 4], 'PixelIterator expects a channel count of 3 or 4'
        assert self.width * self.height * self.channel_count == len(self.pixels), \
            f'PixelIterator: width x height * channel_count != len(pixels) for Image {image.path}'

    def get_color(self, start_index):
        r, g, b, *a = self.pixels[start_index:start_index + self.channel_count]
        r, g, b = [gamma_correct(c) for c in (r, g, b)]
        # a is a list of length 0 (when there are 3 channels) or length 1 (when there are 4 channels).
        a = a[0] if len(a) == 1 else 1  # use 1 as the default value for every pixel when there are 3 channels
        return round_color_tuple((r, g, b, a))

    def __iter__(self):
        if self.analyse_all_pixels:
            for x in range(self.width):
                for y in range(self.height):
                    start_index = (y * self.width + x) * self.channel_count
                    yield self.get_color(start_index=start_index)
        else:
            step = 45  # 45 * 45 = 2025 so this gives a ~2000 pixel sample
            x_step = self.width / step
            y_step = self.height / step
            half_x_step = x_step / 2
            half_y_step = y_step / 2

            for x in range(step):
                for y in range(step):
                    x_co = int(x * x_step + half_x_step)
                    y_co = int(y * y_step + half_y_step)
                    start_index = x_co * y_co * self.channel_count
                    yield self.get_color(start_index=start_index)
