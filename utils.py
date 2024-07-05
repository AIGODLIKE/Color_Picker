import copy

import sys
if '3.10' in sys.version:
    from .extern.imgui_bundle3_10.imgui_bundle import imgui
else:
    from .extern.imgui_bundle3_11.imgui_bundle import imgui
import bpy
import os
def get_path():
    return os.path.dirname((os.path.realpath(__file__)))

def get_name():
    return os.path.basename(get_path())

def get_prefs():
    return bpy.context.preferences.addons[get_name()].preferences
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
        elif mode == 'VERTEX_GPENCIL':
            # 在 Grease Pencil 绘制模式下
            bpy.context.tool_settings.gpencil_vertex_paint.brush.color.hsv = color
        elif mode == 'SCULPT':
            bpy.data.brushes['Paint'].color.hsv = color
        elif bpy.context.area.spaces.active.ui_mode == 'PAINT':
            bpy.context.tool_settings.image_paint.brush.color.hsv = color
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
        elif mode == 'VERTEX_GPENCIL':
            # 在 Grease Pencil 绘制模式下
            bpy.context.tool_settings.gpencil_vertex_paint.brush.color = color
        elif mode == 'SCULPT':
            bpy.data.brushes['Paint'].color = color
        elif bpy.context.area.spaces.active.ui_mode == 'PAINT':
            bpy.context.tool_settings.image_paint.brush.color = color
def set_brush_strength_based_on_mode(strength=None):
    # 获取当前的模式
    mode = bpy.context.object.mode

    # 根据不同的模式获取笔刷颜色
    if mode == 'VERTEX_PAINT':
        # 在顶点绘制模式下
        bpy.context.tool_settings.vertex_paint.brush.strength=strength

    elif mode == 'TEXTURE_PAINT':
        # 在纹理绘制模式下
        bpy.context.tool_settings.image_paint.brush.strength=strength

    elif mode == 'PAINT_GPENCIL':
        # 在 Grease Pencil 绘制模式下
        bpy.context.tool_settings.gpencil_paint.brush.strength=strength
    elif mode == 'VERTEX_GPENCIL':
        # 在 Grease Pencil 绘制模式下
        bpy.context.tool_settings.gpencil_vertex_paint.brush.strength = strength
    elif mode == 'SCULPT':
        bpy.data.brushes['Paint'].strength = strength
    elif bpy.context.area.spaces.active.ui_mode == 'PAINT':
        brush = bpy.context.tool_settings.image_paint.brush.strength = strength
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
        elif mode == 'VERTEX_GPENCIL':
            # 在 Grease Pencil 绘制模式下
            brush = bpy.context.tool_settings.gpencil_vertex_paint.brush
            color = brush.color
        elif mode=='SCULPT':
            brush = bpy.data.brushes['Paint']
            color = brush.color
        elif bpy.context.area.spaces.active.ui_mode=='PAINT':
            brush = bpy.context.tool_settings.image_paint.brush
            color = brush.color
        return color


def get_brush_strength_based_on_mode():
    # 获取当前的模式
    mode = bpy.context.object.mode

    # 根据不同的模式获取笔刷颜色
    if mode == 'VERTEX_PAINT':
        # 在顶点绘制模式下
        brush = bpy.context.tool_settings.vertex_paint.brush
        strength = brush.strength
    elif mode == 'TEXTURE_PAINT':
        # 在纹理绘制模式下
        brush = bpy.context.tool_settings.image_paint.brush
        strength = brush.strength
    elif mode == 'PAINT_GPENCIL':
        # 在 Grease Pencil 绘制模式下
        brush = bpy.context.tool_settings.gpencil_paint.brush
        strength = brush.strength
    elif mode == 'VERTEX_GPENCIL':
        # 在 Grease Pencil 绘制模式下
        brush = bpy.context.tool_settings.gpencil_vertex_paint.brush
        strength = brush.strength
    elif mode == 'SCULPT':
        brush = bpy.data.brushes['Paint']
        strength = brush.strength
    elif bpy.context.area.spaces.active.ui_mode == 'PAINT':
        brush = bpy.context.tool_settings.image_paint.brush
        strength = brush.strength
    return strength

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


def register_keymaps(keylist):
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    keymaps = []

    if kc:

        for item in keylist:
            keymap = item.get("keymap")
            space_type = item.get("space_type", "EMPTY")

            if keymap:
                km = kc.keymaps.new(name=keymap, space_type=space_type)

                if km:
                    idname = item.get("idname")
                    type = item.get("type")
                    value = item.get("value")

                    shift = item.get("shift", False)
                    ctrl = item.get("ctrl", False)
                    alt = item.get("alt", False)

                    kmi = km.keymap_items.new(idname, type, value, shift=shift, ctrl=ctrl, alt=alt)

                    if kmi:
                        properties = item.get("properties")

                        if properties:
                            for name, value in properties:
                                setattr(kmi.properties, name, value)

                        active = item.get("active", True)
                        kmi.active = active

                        keymaps.append((km, kmi))
    else:
        print("WARNING: Keyconfig not availabe, skipping color picker keymaps")

    return keymaps
def unregister_keymaps(keymaps):
    for km, kmi in keymaps:
        km.keymap_items.remove(kmi)
