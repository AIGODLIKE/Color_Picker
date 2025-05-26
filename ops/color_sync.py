import bpy
from mathutils import Color

from ..utils import get_tool_prop


class ColorSync:

    @staticmethod
    def get_color(context: "bpy.types.Context") -> "Color|None":
        prop = get_tool_prop(context)
        if prop:
            if color := getattr(prop, "color"):
                return color
        return Color()

    def set_color(self, context, color, sync_to_hsv=False):
        prop = get_tool_prop(context)
        if getattr(prop, "color"):
            setattr(prop, "color", color)
            self.start_color = color
            self.add_palettes_color(color)
            if sync_to_hsv:
                self.start_hsv = color.hsv

    def from_start_hsv_get_rgb(self):
        import colorsys
        hsv = self.start_hsv
        return colorsys.hsv_to_rgb(*hsv)

    def set_hsv(self, context, h, s, v):
        import colorsys
        color = colorsys.hsv_to_rgb(h, s, v)
        print("set_hsv", h, s, v, end=None)
        self.set_color(context, Color(color))

    def add_palettes_color(self, color):
        """向色盘添加一个颜色"""

        cl = len(color)
        alpha = 1
        if cl == 3:
            r, g, b = color
        elif cl == 4:
            r, g, b, alpha = color
        else:
            Exception("Color Error")

        if palette := self.get_palette():
            nc = palette.colors.new()
            nc.color = Color((r, g, b))
            nc.strength = alpha

    @staticmethod
    def get_palette():
        name = "Picker Color"
        palettes = bpy.data.palettes
        if palette := palettes.get(name):
            return palette
        return palettes.new(name)

    @staticmethod
    def get_size(context):
        prop = get_tool_prop(context)
        if size := getattr(prop, "size"):
            return size
        return -1

    @staticmethod
    def set_size(context, size):
        prop = get_tool_prop(context)
        if getattr(prop, "size"):
            setattr(prop, "size", size)

    @staticmethod
    def get_strength(context):
        prop = get_tool_prop(context)
        if strength := getattr(prop, "strength"):
            return strength
        return -1

    @staticmethod
    def set_strength(context, strength):
        prop = get_tool_prop(context)
        if getattr(prop, "strength"):
            setattr(prop, "strength", strength)
