import bpy

from mathutils import Color


def get_pref():
    return bpy.context.preferences.addons[__package__].preferences


def get_context_brush_color(context: bpy.types.Context):
    mode = context.object.mode
    color = Color()
    # 根据不同的模式获取笔刷颜色
    if mode == 'VERTEX_PAINT':
        # 在顶点绘制模式下
        brush = bpy.context.tool_settings.vertex_paint.brush
        color = brush.color
    elif mode == 'TEXTURE_PAINT':
        # 在纹理绘制模式下
        brush = bpy.context.tool_settings.image_paint.brush
        color = brush.color
    elif mode == 'PAINT_GPENCIL':
        # 在 Grease Pencil 绘制模式下
        brush = bpy.context.tool_settings.gpencil_paint.brush
        color = brush.color
    elif mode == 'VERTEX_GPENCIL':
        # 在 Grease Pencil 绘制模式下
        brush = bpy.context.tool_settings.gpencil_vertex_paint.brush
        color = brush.color
    elif mode == 'SCULPT':
        # from bl_ui.properties_paint_common import UnifiedPaintPanel
        # paint = UnifiedPaintPanel.paint_settings(bpy.context)
        # print("paint", paint)
        # print(dir(paint))
        # brush = bpy.data.brushes['Paint']
        # bpy.data.scenes["Scene"].tool_settings.unified_paint_settings.color

        color = bpy.context.tool_settings.unified_paint_settings.color
    elif bpy.context.area.spaces.active.ui_mode == 'PAINT':
        brush = bpy.context.tool_settings.image_paint.brush
        color = brush.color
    return color
