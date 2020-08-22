import os
import re
import threading
import sys
import textwrap

class utils:

    def escape(char, *params):
        return f"\033[{';'.join(params)}{char}"

    def map_invert(map):
        result = []
        for i in range(len(map[0])):
            res = []
            for data in map:
                res.append(data[i])
            result.append(res)
        return result

class escapes:

    def up(n=1):
        return utils.escape("A", str(n))

    def down(n=1):
        return utils.escape("B", str(n))

    def back(n=1):
        return utils.escape("D", str(n))

    def forward(n=1):
        return utils.escape("C", str(n))

    def setline(line):
        return utils.escape("d", str(line))

    def setcolumn(column):
        return utils.escape("G", str(column))

    def set_position(x, y):
        return escapes.setline(y) + escapes.setcolumn(x)

    def clearline(between=False):
        if between:
            return utils.escape("K")
        else:
            return utils.escape("K", "2")

    def clear():
        return utils.escape("J", "2")

    def get_size():
        columns, rows = os.get_terminal_size()
        return columns, rows

    def delchar():
        return utils.escape("X", "1")

    def store():
        return utils.escape("s")

    def restore():
        return utils.escape("u")

    def underline(on=True):
        if on:
            return utils.escape("m", "4")
        else:
            return utils.escape("m", "24")

    def blink(on=True):
        if on:
            return utils.escape("m", "5")
        else:
            return utils.escape("m", "25")

    def reverse(on=True):
        if on:
            return utils.escape("m", "7")
        else:
            return utils.escape("m", "27")

    def reset():
        return utils.escape("m", "0")

    def black(light=False, background=False):
        if light and not background:
            code = "90"
        elif background:
            code = "40"
        else:
            code = "30"
        return utils.escape("m", code)

    def red(light=False, background=False):
        if light and not background:
            code = "91"
        elif background:
            code = "41"
        else:
            code = "31"
        return utils.escape("m", code)

    def green(light=False, background=False):
        if light and not background:
            code = "92"
        elif background:
            code = "42"
        else:
            code = "32"
        return utils.escape("m", code)

    def yellow(light=False, background=False):
        if light and not background:
            code = "93"
        elif background:
            code = "43"
        else:
            code = "33"
        return utils.escape("m", code)

    def blue(light=False, background=False):
        if light and not background:
            code = "94"
        elif background:
            code = "44"
        else:
            code = "34"
        return utils.escape("m", code)

    def magenta(light=False, background=False):
        if light and not background:
            code = "95"
        elif background:
            code = "45"
        else:
            code = "35"
        return utils.escape("m", code)

    def cyan(light=False, background=False):
        if light and not background:
            code = "96"
        elif background:
            code = "46"
        else:
            code = "36"
        return utils.escape("m", code)

    def white(light=False, background=False):
        if light and not background:
            code = "97"
        elif background:
            code = "47"
        else:
            code = "37"
        return utils.escape("m", code)

    def color(hex, background=False):
        rgb = list(textwrap.wrap(hex.lstrip("#"), 2))
        if len(rgb) == 2:
            rgb.append("0")
        elif len(rgb) == 1:
            rgb.append("0")
            rgb.append("0")
        if not background:
            return "\033[38;2;" + str(int(rgb[0], 16)) + ";" + str(int(rgb[1], 16)) + ";" + str(int(rgb[2], 16)) + "m"
        else:
            return "\033[48;2;" + str(int(rgb[0], 16)) + ";" + str(int(rgb[1], 16)) + ";" + str(int(rgb[2], 16)) + "m"

class engine:

    def __init__(self, background_color=None, text_color=None):
        os.system("")
        print(escapes.clear(), end="", flush=True)

        columns, rows = escapes.get_size()
        self.size = (columns, rows)
        if not background_color:
            background_color = color.bg_black
        if not text_color:
            text_color = color.white
        self.default_pixel = [background_color, text_color, " "]
        self.pixels = [[list(self.default_pixel) for _ in range(rows)] for _ in range(columns)]
        self.previous_pixels = [[list(self.default_pixel) for _ in range(rows)] for _ in range(columns)]
        self.update_lock = threading.Lock()

    def set(self, x: int, y: int, background_color: int=None, text_color: int=None, text: str=None) -> None:
        if x < len(self.pixels) and y < len(self.pixels[0]):
            if text:
                if len(text) == 1:
                    self.pixels[x][y][2] = text
                else:
                    raise Exception("Pixel text must be only one char.")
                    return
            if background_color:
                self.pixels[x][y][0] = background_color
            if text_color:
                self.pixels[x][y][1] = text_color
        else:
            raise Exception("That pixel doesn't exist.")

    def reset_frame(self) -> None:
        columns, rows = escapes.get_size()
        self.size = (columns, rows)
        self.pixels = [[list(self.default_pixel) for _ in range(rows)] for _ in range(columns)]
        previous_pixels = list(self.pixels)
        for key, pixel in enumerate(self.previous_pixels):
            previous_pixels[key] = pixel
        self.previous_pixels = list(previous_pixels)

    def reset_pixel(self, x, y) -> None:
        self.pixels[x][y] = self.default_pixel

    def update_pixels(self, start_x: int, start_y: int, stop_x: int, stop_y: int) -> None:
        output = ""
        for x, pixels in enumerate(self.pixels[start_x:(stop_x+1)]):
            for y, pixel in enumerate(pixels[start_y:(stop_y+1)]):
                output += escapes.set_position(x + 1, y + 1)
                self.previous_pixels[x][y] = pixel
                if type(pixel[0]) == int:
                    output += utils.escape("m", str(pixel[0]))
                else:
                    output += escapes.color(str(pixel[0]), background=True)
                if type(pixel[1]) == int:
                    output += utils.escape("m", str(pixel[1]))
                else:
                    output += escapes.color(str(pixel[1]))
                output += pixel[2]
        output += escapes.set_position(self.size[0], self.size[1])
        output += escapes.reset()

        with self.update_lock:
            sys.stdout.write(output)
            sys.stdout.flush()

    def update_screen(self) -> None:
        output = ""
        output += escapes.set_position(1, 1)
        pos = [1, 1]
        prev_colors = [None, None]
        pixels_map = utils.map_invert(self.pixels)
        for y, pixels in enumerate(pixels_map):
            for x, pixel in enumerate(pixels):
                if self.previous_pixels[x][y] == pixel:
                    continue
                self.previous_pixels[x][y] = pixel
                if pos[0] == self.size[0]:
                    next_pos = [0, pos[1]+1]
                else:
                    next_pos = [pos[0]+1, pos[1]]
                if pos != [x + 1, y + 1]:
                    output += escapes.set_position(x + 1, y + 1)
                    if (x + 1) == self.size[0]:
                        pos = [0, y+2]
                    else:
                        pos = [x+2, y+1]
                else:
                    pos = next_pos
                if prev_colors[0] != pixel[0]:
                    prev_colors[0] = pixel[0]
                    if type(pixel[0]) == int:
                        output += utils.escape("m", str(pixel[0]))
                    else:
                        output += escapes.color(str(pixel[0]), background=True)
                if prev_colors[1] != pixel[1]:
                    prev_colors[1] = pixel[1]
                    if type(pixel[1]) == int:
                        output += utils.escape("m", str(pixel[1]))
                    else:
                        output += escapes.color(str(pixel[1]))
                output += pixel[2]
        output += escapes.set_position(self.size[0], self.size[1])
        output += escapes.reset()

        with self.update_lock:
            sys.stdout.write(output)
            sys.stdout.flush()

class color:

    black = 30
    red = 31
    green = 32
    yellow = 33
    blue = 34
    magenta = 35
    cyan = 36
    white = 37

    light_black = 90
    light_red = 91
    light_green = 92
    light_yellow = 93
    light_blue = 94
    light_magenta = 95
    light_cyan = 96
    light_white = 97

    bg_black = 40
    bg_red = 41
    bg_green = 42
    bg_yellow = 43
    bg_blue = 44
    bg_magenta = 45
    bg_cyan = 46
    bg_white = 47

    def hex(color):
        return color
