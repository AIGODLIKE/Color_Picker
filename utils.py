import bpy


def get_pref():
    return bpy.context.preferences.addons[__package__].preferences


def get_tool_prop(context):
    """bpy.data.scenes["Scene"].tool_settings.unified_paint_settings.color
    # bpy.data.scenes["Scene"].tool_settings.unified_paint_settings.color
    """
    tool_settings = context.tool_settings
    if unified_paint_settings := getattr(tool_settings, "unified_paint_settings"):
        return unified_paint_settings
    return None


def get_brush(context):
    """
    bpy.data.brushes["Paint Hard", "C:\\Program Files\\Blender Foundation\\Blender 4.4\\4.4\\datafiles\\assets\\brushes\\essentials_brushes-mesh_sculpt.blend"].strength
    bpy.data.brushes["Average", "C:\\Program Files\\Blender Foundation\\Blender 4.4\\4.4\\datafiles\\assets\\brushes\\essentials_brushes-mesh_weight.blend"].strength
    """
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

