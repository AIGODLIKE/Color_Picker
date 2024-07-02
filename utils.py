import copy

from .extern.imgui_bundle import imgui
import bpy

def get_imgui_widget_center():
    h=116
    return imgui.ImVec2(imgui.get_mouse_pos().x-h,imgui.get_mouse_pos().y-h)
def set_brush_color_based_on_mode(color=None,hsv=None):
    # 获取当前的模式
    mode = bpy.context.object.mode
    if hsv:
        # 根据不同的模式获取笔刷颜色
        if mode == 'VERTEX_PAINT':
            # 在顶点绘制模式下
            bpy.context.tool_settings.vertex_paint.brush.color.hsv = color

        elif mode == 'TEXTURE_PAINT':
            # 在纹理绘制模式下
            bpy.context.tool_settings.image_paint.brush.color.hsv = color

        elif mode == 'PAINT_GPENCIL':
            # 在 Grease Pencil 绘制模式下
            bpy.context.tool_settings.gpencil_paint.brush.color.hsv = color
        elif mode == 'SCULPT':
            bpy.data.brushes['Paint'].color.hsv = color
    else:
        # 根据不同的模式获取笔刷颜色
        if mode == 'VERTEX_PAINT':
            # 在顶点绘制模式下
            bpy.context.tool_settings.vertex_paint.brush.color=color

        elif mode == 'TEXTURE_PAINT':
            # 在纹理绘制模式下
            bpy.context.tool_settings.image_paint.brush.color=color

        elif mode == 'PAINT_GPENCIL':
            # 在 Grease Pencil 绘制模式下
            bpy.context.tool_settings.gpencil_paint.brush.color=color
        elif mode == 'SCULPT':
            bpy.data.brushes['Paint'].color = color
def get_brush_color_based_on_mode():
        # 获取当前的模式
        mode = bpy.context.object.mode

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
        elif mode=='SCULPT':
            brush = bpy.data.brushes['Paint']
            color = brush.color
        return color

def exchange_brush_color_based_on_mode(exchange=None):
    mode = bpy.context.object.mode
    if exchange:
        # 根据不同的模式获取笔刷颜色
        if mode == 'VERTEX_PAINT':
            # 在顶点绘制模式下
            tmp=copy.deepcopy(bpy.context.tool_settings.vertex_paint.brush.color)
            bpy.context.tool_settings.vertex_paint.brush.color= bpy.context.tool_settings.vertex_paint.brush.secondary_color
            bpy.context.tool_settings.vertex_paint.brush.secondary_color=tmp

        elif mode == 'TEXTURE_PAINT':
            # 在纹理绘制模式下
            tmp = copy.deepcopy(bpy.context.tool_settings.image_paint.brush.color)
            bpy.context.tool_settings.image_paint.brush.color = bpy.context.tool_settings.image_paint.brush.secondary_color
            bpy.context.tool_settings.image_paint.brush.secondary_color=tmp

        elif mode == 'PAINT_GPENCIL':
            # 在 Grease Pencil 绘制模式下
            tmp = copy.deepcopy(bpy.context.tool_settings.gpencil_paint.brush.color)
            bpy.context.tool_settings.gpencil_paint.brush.color = bpy.context.tool_settings.gpencil_paint.brush.secondary_color
            bpy.context.tool_settings.gpencil_paint.brush.secondary_color=tmp
        elif mode == 'SCULPT':
            tmp = copy.deepcopy(bpy.data.brushes['Paint'].color)
            bpy.data.brushes['Paint'].color = bpy.data.brushes['Paint'].secondary_color
            bpy.data.brushes['Paint'].secondary_color=tmp