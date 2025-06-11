import bpy


def get_pref():
    return bpy.context.preferences.addons[__package__].preferences


def get_tool_prop(context):
    tool_settings = context.tool_settings
    if unified_paint_settings := getattr(tool_settings, "unified_paint_settings"):
        return unified_paint_settings
    return None


def get_brush(context):
    mode = context.object.mode
    tool_settings = context.tool_settings
    if mode == "VERTEX_PAINT":  # 在顶点绘制模式下
        brush = tool_settings.vertex_paint.brush
        return brush
    elif mode == "TEXTURE_PAINT":  # 在纹理绘制模式下
        brush = tool_settings.image_paint.brush
        return brush
    elif mode == "WEIGHT_PAINT":
        brush = tool_settings.weight_paint.brush
        return brush
    elif mode == "VERTEX_GPENCIL":  # 在 Grease Pencil 绘制模式下
        brush = tool_settings.gpencil_vertex_paint.brush
        return brush
    elif mode == "SCULPT":
        brush = tool_settings.sculpt.brush
        return brush
    elif mode == "PAINT_GPENCIL":  # 在 Grease Pencil 绘制模式下
        brush = tool_settings.gpencil_paint.brush
        return brush

    elif mode == "PAINT_GREASE_PENCIL":
        brush = tool_settings.gpencil_paint.brush
        return brush
    elif mode == "VERTEX_GREASE_PENCIL":
        brush = tool_settings.gpencil_vertex_paint.brush
        return brush
    elif mode == "SCULPT_GREASE_PENCIL":
        brush = tool_settings.gpencil_paint.brush
        return brush
    return None


def rgb_to_hex(rgb):
    """将 RGB 元组 (0-1范围) 转换为十六进制字符串"""
    return f"#{int(rgb[0] * 255):02X}{int(rgb[1] * 255):02X}{int(rgb[2] * 255):02X}"


def im_clamp(v, mn, mx):
    return max(mn, min(mx, v))


def im_saturate(f):
    return 0.0 if f < 0.0 else 1.0 if f > 1.0 else f


def im_lerp(a, b, t):
    import imgui
    return imgui.Vec2(a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t)


def im_length_sqr(lhs):
    return (lhs.x * lhs.x) + (lhs.y * lhs.y)
