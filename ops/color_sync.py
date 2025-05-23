from mathutils import Color


class ColorSync:
    def get_color_prop(self, context):
        mode = context.object.mode
        if mode == 'VERTEX_PAINT':
            # 在顶点绘制模式下
            brush = bpy.context.tool_settings.vertex_paint.brush
            return brush, "color"
        elif mode == 'TEXTURE_PAINT':
            # 在纹理绘制模式下
            brush = bpy.context.tool_settings.image_paint.brush
            return brush, "color"
        elif mode == 'PAINT_GPENCIL':
            # 在 Grease Pencil 绘制模式下
            brush = bpy.context.tool_settings.gpencil_paint.brush
            return brush, "color"
        elif mode == 'VERTEX_GPENCIL':
            # 在 Grease Pencil 绘制模式下
            brush = bpy.context.tool_settings.gpencil_vertex_paint.brush
            return brush, "color"
        elif mode == 'SCULPT':
            unified_paint_settings = bpy.context.tool_settings.unified_paint_settings
            return unified_paint_settings, "color"
        return None, None

    def get_color(self, context):
        prop, name = self.get_color_prop(context)
        if color := getattr(prop, name):
            return color
        return Color()

    def set_color(self, context, color):
        prop, name = self.get_color_prop(context)
        if getattr(prop, name):
            setattr(prop, name, color)

    def get_hsv(self, context):
        ...

    def set_hsv(self, context):
        ...

    @staticmethod
    def picker_color(color):
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
