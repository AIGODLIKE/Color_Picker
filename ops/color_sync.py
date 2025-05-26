from mathutils import Color


def get_color_prop(context):
    """bpy.data.scenes["Scene"].tool_settings.unified_paint_settings.color"""
    mode = context.object.mode
    tool_settings = context.tool_settings
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
        print("get_color", prop, name)
        if prop and name:
            if color := getattr(prop, name):
                return color
        return Color()

    @staticmethod
    def set_color(context, color):
        prop, name = get_color_prop(context)
        if getattr(prop, name):
            setattr(prop, name, color)

    def get_hsv(self, context):
        ...

    def set_hsv(self, context):
        ...

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
