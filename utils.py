import bpy

from mathutils import Color


def get_pref():
    return bpy.context.preferences.addons[__package__].preferences


def get_context_brush_color(context: bpy.types.Context):
    mode = context.object.mode
    color = Color()
    return color
    # 根据不同的模式获取笔刷颜色
    # elif bpy.context.area.spaces.active.ui_mode == 'PAINT':
    #     brush = bpy.context.tool_settings.image_paint.brush
    #     color = brush.color
    return color
