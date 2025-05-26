from mathutils import Color


def get_color_prop(context):
    """bpy.data.scenes["Scene"].tool_settings.unified_paint_settings.color
    # bpy.data.scenes["Scene"].tool_settings.unified_paint_settings.color
    """
    mode = context.object.mode
    tool_settings = context.tool_settings

    if unified_paint_settings := getattr(tool_settings, "unified_paint_settings"):
        return unified_paint_settings, "color"

    if mode == 'VERTEX_PAINT':
        # 在顶点绘制模式下
        brush = tool_settings.vertex_paint.brush
        return brush, "color"
    elif mode == 'TEXTURE_PAINT':
        # 在纹理绘制模式下
        brush = tool_settings.image_paint.brush
        return brush, "color"
    elif mode == 'PAINT_GPENCIL':
        # 在 Grease Pencil 绘制模式下
        brush = tool_settings.gpencil_paint.brush
        return brush, "color"
    elif mode == 'VERTEX_GPENCIL':
        # 在 Grease Pencil 绘制模式下
        brush = tool_settings.gpencil_vertex_paint.brush
        return brush, "color"
    elif mode == 'SCULPT':
        unified_paint_settings = tool_settings.unified_paint_settings
        return unified_paint_settings, "color"
    return None, None


class ColorSync:

    @staticmethod
    def get_color(context: "bpy.types.Context") -> "Color|None":
        prop, name = get_color_prop(context)
        if prop and name:
            if color := getattr(prop, name):
                print("get_color", prop, name, color)
                return color
        return Color()

    def set_color(self, context, color, sync_to_hsv=False):
        prop, name = get_color_prop(context)
        if getattr(prop, name):
            print("set_color", prop, name, color)
            setattr(prop, name, color)
            self.start_color = color
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

    @staticmethod
    def add_palettes_color(color):
        """向色盘添加一个颜色"""
        name = "Picker Color"
        palettes = bpy.data.palettes

        cl = len(color)
        alpha = 1
        if cl == 3:
            r, g, b = color
        elif cl == 4:
            r, g, b, alpha = color
        else:
            Exception("Color Error")

        if palette := palettes.get(name, palettes.new(name)):
            nc = palette.colors.new()
            nc.color = Color((r, g, b))
            nc.value = alpha
