import math

import bpy
from mathutils import Color

from ..utils import rgb_to_hex

color_edit_active_component = None


def im_clamp(v, mn, mx):
    return max(mn, min(mx, v))


def color_edit_restore_hs(color, H, S, V):
    import imgui
    gc = imgui.get_current_context()
    assert gc.color_edit_current_id != 0, 'ColorEditCurrentID should not be zero'
    if (
            gc.color_edit_saved_id != gc.color_edit_current_id or gc.color_edit_saved_color != imgui.color_convert_float4_to_u32(
        color[0], color[1], color[2], 0)):
        pass
    # return
    if (S == 0.0 or (H == 0.0 and gc.color_edit_saved_hue == 1)):
        H = gc.color_edit_saved_hue
    if V == 0.0:
        S = gc.color_edit_saved_sat
    return H, S, V


def color_edit_restore_h(color, H):
    import imgui
    gc = imgui.get_current_context()
    assert gc.color_edit_current_id != 0
    if gc.color_edit_saved_id != gc.color_edit_current_id or gc.color_edit_saved_color != imgui.color_convert_float4_to_u32(
            color[0], color[1], color[2], 0):
        return H
    return gc.color_edit_saved_hue if gc.color_edit_saved_hue is not None else H


def get_wheeL_tri(mouse_pos):
    import imgui

    sv_picker_size = 256
    square_sz = 19
    bars_width = square_sz
    picker_pos = imgui.Vec2(mouse_pos[0] - 127, mouse_pos[1] + 110)
    wheel_thickness = sv_picker_size * 0.08
    wheel_r_outer = sv_picker_size * 0.50
    wheel_r_inner = wheel_r_outer - wheel_thickness
    wheel_center = imgui.Vec2(picker_pos.x + (sv_picker_size + bars_width) * 0.5,
                              picker_pos.y - sv_picker_size * 0.5)

    triangle_r = wheel_r_inner - int(sv_picker_size * 0.027)
    triangle_pa = imgui.Vec2(triangle_r, 0.0)  # Hue point.
    triangle_pc = imgui.Vec2(triangle_r * -0.5,
                             triangle_r * -0.866025)  # White point.-0.5 和 -0.866025 分别是 cos(120°) 和 sin(120°) 的值。
    triangle_pb = imgui.Vec2(triangle_r * -0.5, triangle_r * +0.866025)
    tra = (wheel_center[0] + triangle_pa.x, wheel_center[1] + triangle_pa.y)
    trb = (wheel_center[0] + triangle_pb.x, wheel_center[1] + triangle_pb.y)
    trc = (wheel_center[0] + triangle_pc.x, wheel_center[1] + triangle_pc.y)
    a0 = (wheel_center[0] + 0, wheel_center[1] + triangle_pa.y)
    b0 = (wheel_center[0] + triangle_pb.x, wheel_center[1] + triangle_pb.y)
    b2 = (wheel_center[0] + triangle_pa.x, wheel_center[1] + triangle_pa.y)
    b4 = (wheel_center[0] + triangle_pb.x, wheel_center[1] + triangle_pc.y)
    c0 = (wheel_center[0] + triangle_pc.x, wheel_center[1] + triangle_pa.y)
    c1 = (wheel_center[0] + triangle_r * 0.25, wheel_center[1] + triangle_pb.y / 2)
    c3 = (wheel_center[0] + triangle_r * 0.25, wheel_center[1] - triangle_pb.y / 2)
    list = [
        # [a0, b0, c0],
        # [a0, b0, c1],
        # [a0, b2, c1],
        # [a0, b2, c3],
        # [a0, b4, c3],
        # [a0, b4, c0],
        [tra, trb, trc],
    ]
    return list


def convert_hsv2rgb32_color3(h, s, v):
    import colorsys
    import imgui
    """ Convert HSV to RGB format and get ImU32 color value. """
    r, g, b = colorsys.hsv_to_rgb(h, s, v)  # Convert HSV to RGB

    return imgui.color_convert_float4_to_u32(r, g, b, 1.0)


class ColorBar:
    """颜色条"""
    slider_width = 1000

    def __init__(self, draw_func):
        self.draw_func = draw_func
        self.draw()

    def draw(self):
        import imgui

        with imgui.begin_group():
            imgui.push_style_color(imgui.COLOR_FRAME_BACKGROUND, 1 / 7.0, 0.6, 1, 0)
            imgui.push_style_color(imgui.COLOR_FRAME_BACKGROUND_HOVERED, 1 / 7.0, .7, 1, 0)
            imgui.push_style_color(imgui.COLOR_FRAME_BACKGROUND_ACTIVE, 1.0, 1.0, 1.0, 0)
            imgui.push_style_color(imgui.COLOR_SLIDER_GRAB, 0.9, 0.9, 0.9, 0.0)
            imgui.push_style_color(imgui.COLOR_SLIDER_GRAB_ACTIVE, 0.9, 0.9, 0.9, 0.0)

            gradient_size = [imgui.calculate_item_width(), 20]

            start_pos = imgui.get_cursor_pos()
            p0 = imgui.get_cursor_screen_pos()
            p1 = p0.x + gradient_size[0], p0.y + gradient_size[1]

            value = self.draw_func(p0, p1)

            x1 = p0[0] + gradient_size[0] * value
            x2 = p0[0] + gradient_size[0] * value
            y1, y2 = p0[1] - 1, p1[1] - 1
            color_a = imgui.color_convert_float4_to_u32(0.2, 0.2, 0.2, 1.0)
            color_b = imgui.color_convert_float4_to_u32(0.9, 0.9, 0.9, 1.0)
            imgui.set_cursor_pos(start_pos)
            imgui.get_window_draw_list().add_line(x1, y1, x2, y2, color_a, 4)
            imgui.set_cursor_pos(start_pos)
            imgui.get_window_draw_list().add_line(x1, y1, x2, y2, color_b, 2)

            imgui.pop_style_color(5)


class ColorWidget:
    def draw_color_picker_wheel(self, picker_hue_wheel=False):
        import imgui

        gc = imgui.get_current_context()
        io = gc.io
        style = gc.style
        draw_list = imgui.get_window_draw_list()
        window = imgui.get_window()

        # 唯一标识符
        imgui.push_id(self.bl_idname + "draw_color_picker_wheel")
        imgui.begin_group()

        # 当前窗口的顶部ID将作为当前颜色编辑器的ID
        set_current_color_edit_id = (gc.color_edit_current_id == 0)
        if set_current_color_edit_id:
            gc.color_edit_current_id = window.id_stack.__getitem__(window.id_stack.size() - 1)

        # 设置
        picker_pos = imgui.Vec2(window.dc.cursor_pos.x, window.dc.cursor_pos.y)

        square_sz = imgui.get_frame_height()

        bars_width = square_sz

        sv_picker_size = max(bars_width * 1, 256)
        bar0_pos_x = picker_pos.x + sv_picker_size + style.item_inner_spacing.x

        wheel_thickness = sv_picker_size * 0.08
        wheel_r_outer = sv_picker_size * 0.50
        wheel_r_inner = wheel_r_outer - wheel_thickness
        wheel_center = imgui.Vec2(picker_pos.x + (sv_picker_size + bars_width) * 0.5,
                                  picker_pos.y + sv_picker_size * 0.5)
        triangle_r = wheel_r_inner - int(sv_picker_size * 0.027)
        triangle_pa = imgui.Vec2(triangle_r, 0.0)
        triangle_pc = imgui.Vec2(triangle_r * -0.5, triangle_r * -0.866025)
        triangle_pb = imgui.Vec2(triangle_r * -0.5, triangle_r * +0.866025)

        sqrt2 = 1.4142135
        quad_size = 2 * triangle_r / sqrt2
        offset_l_up = imgui.Vec2(triangle_r / -sqrt2, triangle_r / -sqrt2)
        offset_r_bot = imgui.Vec2(triangle_r / sqrt2, triangle_r / sqrt2)

        color = self.start_color
        h = color.hsv[0]
        s = color.hsv[1]
        v = color.hsv[2]
        r = color[0]
        g = color[1]
        b = color[2]

        h, s, v = imgui.color_convert_rgb_to_hsv(r, g, b, h, s, v)
        h, s, v = color_edit_restore_hs(color.hsv, h, s, v)

        value_changed = False
        value_changed_h = False
        value_changed_sv = False

        imgui.push_item_flag(imgui.ItemFlags_.no_nav, True)
        global color_edit_active_component
        if picker_hue_wheel:
            imgui.invisible_button('hsv', imgui.Vec2(sv_picker_size + style.item_inner_spacing.x + bars_width,
                                                     sv_picker_size))

            if imgui.is_item_active() and color_edit_active_component is None:
                initial_off = imgui.Vec2(gc.io.mouse_pos_prev.x - wheel_center.x,
                                         gc.io.mouse_pos_prev.y - wheel_center.y)
                initial_dist2 = imgui.internal.im_length_sqr(initial_off)
                if imgui.internal.im_triangle_contains_point(triangle_pa, triangle_pb, triangle_pc, initial_off):
                    color_edit_active_component = 'triangle'
                elif initial_dist2 >= ((wheel_r_inner - 1) * (wheel_r_inner - 1)) and initial_dist2 <= (
                        (wheel_r_outer + 1) * (wheel_r_outer + 1)):
                    color_edit_active_component = 'wheel'

            # 检查当前激活的控件并更新颜色值
            if color_edit_active_component == 'triangle':
                current_off_unrotated = imgui.Vec2(gc.io.mouse_pos.x - wheel_center.x,
                                                   gc.io.mouse_pos.y - wheel_center.y)
                if not imgui.internal.im_triangle_contains_point(triangle_pa, triangle_pb, triangle_pc,
                                                                 current_off_unrotated):
                    current_off_unrotated = imgui.internal.im_triangle_closest_point(triangle_pa, triangle_pb,
                                                                                     triangle_pc,
                                                                                     current_off_unrotated)

                uu, vv, ww = 0.0, 0.0, 0.0
                uu, vv, ww = imgui.internal.im_triangle_barycentric_coords(triangle_pa, triangle_pb, triangle_pc,
                                                                           current_off_unrotated, uu, vv, ww)
                v = im_clamp(1.0 - vv, 0.0001, 1.0)
                s = im_clamp(uu / v, 0.0001, 1.0)
                value_changed = value_changed_sv = True

            elif color_edit_active_component == 'wheel':
                current_off = imgui.Vec2(gc.io.mouse_pos.x - wheel_center.x, gc.io.mouse_pos.y - wheel_center.y)
                h = math.atan2(current_off.y, current_off.x) / math.pi * 0.5
                if h < .0:
                    h += 1.0
                value_changed = value_changed_h = True

            # 重置激活的控件状态
            if not imgui.is_item_active():
                color_edit_active_component = None
        else:
            imgui.invisible_button('hsv', imgui.Vec2(sv_picker_size + style.item_inner_spacing.x + bars_width,
                                                     sv_picker_size))
            # 检查是否需要更新当前激活的控件
            if imgui.is_item_active() and color_edit_active_component is None:
                initial_off = imgui.Vec2(gc.io.mouse_pos_prev.x - wheel_center.x,
                                         gc.io.mouse_pos_prev.y - wheel_center.y)
                initial_dist2 = imgui.internal.im_length_sqr(initial_off)
                quad_l_up = imgui.Vec2(wheel_center.x + offset_l_up.x, wheel_center.y + offset_l_up.y)
                quad_r_bot = imgui.Vec2(wheel_center.x + offset_r_bot.x, wheel_center.y + offset_r_bot.y)

                if (quad_l_up.x <= io.mouse_pos.x <= quad_r_bot.x and
                        quad_l_up.y <= io.mouse_pos.y <= quad_r_bot.y):
                    color_edit_active_component = 'square'
                if initial_dist2 >= ((wheel_r_inner - 1) * (wheel_r_inner - 1)) and initial_dist2 <= (
                        (wheel_r_outer + 1) * (wheel_r_outer + 1)):
                    color_edit_active_component = 'wheel'

            if color_edit_active_component == 'square':
                l_up = imgui.Vec2(wheel_center.x + offset_l_up.x, wheel_center.y + offset_l_up.y)
                s = imgui.internal.im_saturate((io.mouse_pos.x - l_up.x) / (quad_size - 1))
                v = 1.0 - imgui.internal.im_saturate((io.mouse_pos.y - l_up.y) / (quad_size - 1))
                h = color_edit_restore_h(color, h)
                value_changed = value_changed_sv = True

            elif color_edit_active_component == 'wheel':
                current_off = imgui.Vec2(gc.io.mouse_pos.x - wheel_center.x, gc.io.mouse_pos.y - wheel_center.y)
                h = math.atan2(current_off.y, current_off.x) / math.pi * 0.5
                if h < .0:
                    h += 1.0
                value_changed = value_changed_h = True
                # 重置激活的控件状态
            if not imgui.is_item_active():
                color_edit_active_component = None
            imgui.set_cursor_screen_pos(imgui.Vec2(bar0_pos_x, picker_pos.y))

        imgui.pop_item_flag()
        if value_changed_h or value_changed_sv:
            color[0], color[1], color[2] = imgui.color_convert_hsv_to_rgb(h, s, v, color[0], color[1], color[2])
            gc.color_edit_saved_hue = h
            gc.color_edit_saved_sat = s
            gc.color_edit_saved_id = gc.color_edit_current_id
            gc.color_edit_saved_color = imgui.color_convert_float4_to_u32(
                imgui.Vec4(color[0], color[1], color[2], 0.0))

        if value_changed:
            r = color[0]
            g = color[1]
            b = color[2]
            h, s, v = imgui.color_convert_rgb_to_hsv(r, g, b, h, s, v)
            h, s, v = color_edit_restore_hs(color, h, s, v)

        col_black = imgui.color_convert_float4_to_u32(imgui.Vec4(0.0, 0.0, 0.0, 1.0))
        col_white = imgui.color_convert_float4_to_u32(imgui.Vec4(1.0, 1.0, 1.0, 1.0))
        col_midgrey = imgui.color_convert_float4_to_u32(imgui.Vec4(0.5, 0.5, 0.5, 0.0))
        col_hues = [
            imgui.get_color_u32(imgui.Vec4(255, 0, 0, 255)),  # 红色
            imgui.get_color_u32(imgui.Vec4(255, 255, 0, 255)),  # 黄色
            imgui.get_color_u32(imgui.Vec4(0, 255, 0, 255)),  # 绿色
            imgui.get_color_u32(imgui.Vec4(0, 255, 255, 255)),  # 青色
            imgui.get_color_u32(imgui.Vec4(0, 0, 255, 255)),  # 蓝色
            imgui.get_color_u32(imgui.Vec4(255, 0, 255, 255)),  # 品红
            imgui.get_color_u32(imgui.Vec4(255, 0, 0, 255))  # 红色(再次出现以闭合色环)
        ]

        hue_color_f = imgui.Vec4(1, 1, 1, 1)
        rgb = imgui.color_convert_hsv_to_rgb(h, 1, 1, hue_color_f.x, hue_color_f.y, hue_color_f.z)
        hue_color_f = imgui.Vec4(*rgb, 1)

        hue_color32 = imgui.color_convert_float4_to_u32(hue_color_f)
        user_col32_striped_of_alpha = imgui.color_convert_float4_to_u32(imgui.Vec4(r, g, b, 1))

        # 圆环
        aeps = 0.5 / wheel_r_outer
        segment_per_arc = max(4, int(wheel_r_outer / 12))  # 每个弧段的分段数，确保至少为4段或根据外半径计算。
        for n in range(6):
            a0 = n / 6.0 * 2.0 * math.pi - aeps
            a1 = (n + 1) / 6.0 * 2.0 * math.pi + aeps
            vert_start_idx = imgui.get_window_draw_list().vtx_buffer.size()
            imgui.get_window_draw_list().path_arc_to(wheel_center, (wheel_r_inner + wheel_r_outer) * 0.5, a0, a1,
                                                     segment_per_arc)  # 绘制弧形路径
            imgui.get_window_draw_list().path_stroke(col_white, 0, wheel_thickness)
            vert_end_idx = imgui.get_window_draw_list().vtx_buffer.size()
            gradient_p0 = imgui.Vec2(wheel_center.x + math.cos(a0) * wheel_r_inner,
                                     wheel_center.y + math.sin(a0) * wheel_r_inner)  # 起始点的坐标
            gradient_p1 = imgui.Vec2(wheel_center.x + math.cos(a1) * wheel_r_inner,
                                     wheel_center.y + math.sin(a1) * wheel_r_inner)  # 结束点的坐标
            imgui.internal.shade_verts_linear_color_gradient_keep_alpha(imgui.get_window_draw_list(), vert_start_idx,
                                                                        vert_end_idx, gradient_p0, gradient_p1,
                                                                        col_hues[n], col_hues[n + 1])
        cos_hue_angle = math.cos(h * 2.0 * math.pi)
        sin_hue_angle = math.sin(h * 2.0 * math.pi)
        hue_cursor_pos = imgui.Vec2(wheel_center.x + cos_hue_angle * (wheel_r_inner + wheel_r_outer) * 0.5,
                                    wheel_center.y + sin_hue_angle * (wheel_r_inner + wheel_r_outer) * 0.5)

        hue_cursor_rad = wheel_thickness * 0.65 if value_changed_h else wheel_thickness * 0.55
        hue_cursor_segments = imgui.get_window_draw_list()._calc_circle_auto_segment_count(hue_cursor_rad)
        imgui.get_window_draw_list().add_circle_filled(hue_cursor_pos, hue_cursor_rad, hue_color32, hue_cursor_segments)
        imgui.get_window_draw_list().add_circle(hue_cursor_pos, hue_cursor_rad + 1, col_midgrey, hue_cursor_segments)
        imgui.get_window_draw_list().add_circle(hue_cursor_pos, hue_cursor_rad, col_white, hue_cursor_segments)

        # 圆环上的 按钮
        if picker_hue_wheel:
            tra = imgui.Vec2((wheel_center.x + triangle_pa.x), (wheel_center.y + triangle_pa.y))
            trb = imgui.Vec2((wheel_center.x + triangle_pb.x), (wheel_center.y + triangle_pb.y))
            trc = imgui.Vec2((wheel_center.x + triangle_pc.x), (wheel_center.y + triangle_pc.y))
            uv_white = imgui.get_font_tex_uv_white_pixel()

            imgui.get_window_draw_list().prim_reserve(3, 3)
            imgui.get_window_draw_list().prim_vtx(tra, uv_white, hue_color32)
            imgui.get_window_draw_list().prim_vtx(trb, uv_white, col_black)
            imgui.get_window_draw_list().prim_vtx(trc, uv_white, col_white)
            imgui.get_window_draw_list().add_triangle(tra, trb, trc, col_midgrey, 0)
            sv_cursor_pos = imgui.internal.im_lerp(imgui.internal.im_lerp(trc, tra, imgui.internal.im_saturate(s)), trb,
                                                   imgui.internal.im_saturate(1 - v))
        else:  # 绘制正方形
            l_up = imgui.Vec2(wheel_center.x + offset_l_up.x, wheel_center.y + offset_l_up.y)
            r_bot = imgui.Vec2(wheel_center.x + offset_r_bot.x, wheel_center.y + offset_r_bot.y)

            draw_list.add_rect_filled_multicolor(l_up, r_bot, col_white, hue_color32, hue_color32, col_white)
            draw_list.add_rect_filled_multicolor(l_up, r_bot, 0, 0, col_black, col_black)
            imgui.internal.render_frame_border(l_up, r_bot, 0.0)

            sv_cursor_pos = imgui.Vec2(0, 0)
            sv_cursor_pos.x = im_clamp(round(l_up.x + imgui.internal.im_saturate(s) * quad_size), l_up.x + 2,
                                       picker_pos.x + sv_picker_size - 2)
            sv_cursor_pos.y = im_clamp(round(l_up.y + imgui.internal.im_saturate(1 - v) * quad_size), l_up.y + 2,
                                       l_up.y + quad_size - 2)
        sv_cursor_rad = wheel_thickness * 0.55 if value_changed_sv else wheel_thickness * 0.4
        sv_cursor_segments = imgui.get_window_draw_list()._calc_circle_auto_segment_count(sv_cursor_rad)

        imgui.get_window_draw_list().add_circle_filled(sv_cursor_pos, sv_cursor_rad, user_col32_striped_of_alpha,
                                                       sv_cursor_segments)
        imgui.get_window_draw_list().add_circle(sv_cursor_pos, sv_cursor_rad + 1, col_midgrey, sv_cursor_segments)
        imgui.get_window_draw_list().add_circle(sv_cursor_pos, sv_cursor_rad, col_white, sv_cursor_segments)
        imgui.end_group()

        if value_changed and gc.last_item_data.id_ != 0:
            imgui.internal.mark_item_edited(gc.last_item_data.id_)
        if set_current_color_edit_id:
            gc.color_edit_current_id = 0
        imgui.pop_id()

        if value_changed:
            self.set_hsv(bpy.context, h, s, v)
            self.start_hsv = (h, s, v)

    def draw_h_bar(self):
        import imgui

        def draw(p0, p1):
            h, s, v = self.start_hsv

            col_hues = [
                imgui.get_color_u32_rgba(1, 0, 0, 1),  # 红色
                imgui.get_color_u32_rgba(1, 1, 0, 1),  # 黄色
                imgui.get_color_u32_rgba(0, 1, 0, 1),  # 绿色
                imgui.get_color_u32_rgba(0, 1, 1, 1),  # 青色
                imgui.get_color_u32_rgba(0, 0, 1, 1),  # 蓝色
                imgui.get_color_u32_rgba(1, 0, 1, 1),  # 品红
                imgui.get_color_u32_rgba(1, 0, 0, 1)  # 红色(再次出现以闭合色环)
            ]

            segment = imgui.calculate_item_width() / 6
            for c in range(6):
                start = p0[0]
                imgui.get_window_draw_list().add_rect_filled_multicolor(
                    start + c * segment, p0[1],
                    start + (c + 1) * segment, p1[1],
                    col_hues[c],
                    col_hues[c + 1],
                    col_hues[c + 1],
                    col_hues[c])
            changed, h = imgui.slider_float("H ", h, 0.0, 1.0, "", imgui.SLIDER_FLAGS_NO_INPUT)
            if changed:
                self.set_hsv(bpy.context, h, s, v)
                self.start_hsv = (h, s, v)
            return h
        ColorBar(draw)

    def draw_s_bar(self):
        import imgui

        def draw(p0, p1):
            h, s, v = self.start_hsv
            imgui.get_window_draw_list().add_rect_filled_multicolor(p0[0], p0[1],
                                                                    p1[0], p1[1],
                                                                    convert_hsv2rgb32_color3(0, 0, v),
                                                                    convert_hsv2rgb32_color3(h, 1.0, v),
                                                                    convert_hsv2rgb32_color3(h, 1.0, v),
                                                                    convert_hsv2rgb32_color3(0, 0, v)
                                                                    )
            changed, s = imgui.slider_float("S ", s, 0.0, 1.0, "", imgui.SLIDER_FLAGS_NO_INPUT)

            if changed:
                self.set_hsv(bpy.context, h, s, v)
                self.start_hsv = (h, s, v)
            return s
        ColorBar(draw)

    def draw_v_bar(self):
        import imgui

        def draw(p0, p1):
            h, s, v = self.start_hsv
            imgui.get_window_draw_list().add_rect_filled_multicolor(p0[0], p0[1],
                                                                    p1[0], p1[1],
                                                                    convert_hsv2rgb32_color3(0, 0, 0),
                                                                    convert_hsv2rgb32_color3(h, s, 1),
                                                                    convert_hsv2rgb32_color3(h, s, 1),
                                                                    convert_hsv2rgb32_color3(0, 0, 0)
                                                                    )
            changed, v = imgui.slider_float("V", v, 0.0, 1.0, "", imgui.SLIDER_FLAGS_NO_INPUT)
            if changed:
                self.start_hsv = (h, s, v)
                self.set_hsv(bpy.context, h, s, v)
            return v
        ColorBar(draw)

    def draw_r_bar(self):
        import imgui

        def draw(p0, p1):
            draw_list = imgui.get_window_draw_list()
            r, g, b = self.from_start_hsv_get_rgb()

            draw_list.add_rect_filled_multicolor(p0[0], p0[1], p1[0], p1[1],
                                                 imgui.color_convert_float4_to_u32(0, g, b, 1.0),
                                                 imgui.color_convert_float4_to_u32(1, g, b, 1.0),
                                                 imgui.color_convert_float4_to_u32(1, g, b, 1.0),
                                                 imgui.color_convert_float4_to_u32(0, g, b, 1.0),
                                                 )
            changed, r = imgui.slider_float("R ", r, 0.0, 1.0, "", imgui.SLIDER_FLAGS_NO_INPUT)
            if changed:
                self.set_color(bpy.context, Color((r, g, b)), sync_to_hsv=True)
            return r
        ColorBar(draw)

    def draw_g_bar(self):
        import imgui

        def draw(p0, p1):
            r, g, b = self.from_start_hsv_get_rgb()
            imgui.get_window_draw_list().add_rect_filled_multicolor(p0[0], p0[1],
                                                                    p1[0], p1[1],
                                                                    imgui.color_convert_float4_to_u32(
                                                                        r, 0, b, 1.0),
                                                                    imgui.color_convert_float4_to_u32(
                                                                        r, 1, b, 1.0),
                                                                    imgui.color_convert_float4_to_u32(
                                                                        r, 1, b, 1.0),
                                                                    imgui.color_convert_float4_to_u32(
                                                                        r, 0, b, 1.0),
                                                                    )
            changed, g = imgui.slider_float("G ", g, 0.0, 1.0, "", imgui.SLIDER_FLAGS_NO_INPUT)
            if changed:
                self.set_color(bpy.context, Color((r, g, b)), sync_to_hsv=True)
            return g
        ColorBar(draw)

    def draw_b_bar(self):
        import imgui

        def draw(p0, p1):
            r, g, b = self.from_start_hsv_get_rgb()

            imgui.get_window_draw_list().add_rect_filled_multicolor(p0[0], p0[1],
                                                                    p1[0], p1[1],
                                                                    imgui.color_convert_float4_to_u32(
                                                                        r, g, 0, 1.0),
                                                                    imgui.color_convert_float4_to_u32(
                                                                        r, g, 1, 1.0),
                                                                    imgui.color_convert_float4_to_u32(
                                                                        r, g, 1, 1.0),
                                                                    imgui.color_convert_float4_to_u32(
                                                                        r, g, 0, 1.0),
                                                                    )
            changed, b = imgui.slider_float("B ", b, 0.0, 1.0, "", imgui.SLIDER_FLAGS_NO_INPUT)
            if changed:
                self.set_color(bpy.context, Color((r, g, b)), sync_to_hsv=True)
            return b
        ColorBar(draw)

    @staticmethod
    def draw_switch_button():
        import imgui
        from ..utils import get_pref

        window = imgui.internal.get_current_window()
        draw_list = window.draw_list
        start_pos = pos = imgui.get_cursor_pos()
        imgui.set_cursor_pos(start_pos)
        size = 20
        center = imgui.Vec2(pos.x + size / 2, pos.y + size / 2)
        imgui.push_style_color(21, 0, 0, 0, 0.1)
        imgui.push_style_color(22, 0, 0, 0, 0.1)
        imgui.push_style_color(23, 0, 0, 0, 0.1)

        pref = get_pref()
        # 绘制按钮
        if imgui.button(" ", imgui.Vec2(size, size)):
            pref.picker_switch = not pref.picker_switch

        imgui.pop_style_color(3)

        size /= 2
        position = center
        if pref.picker_switch:
            draw_list.add_triangle_filled(
                imgui.Vec2(position[0] + size, position[1] + size),
                imgui.Vec2(position[0] - size, position[1] + size),
                imgui.Vec2(position[0], position[1] - size),
                imgui.color_convert_float4_to_u32(0.6, .6, .6, 0.05)
            )
        else:
            draw_list.add_rect_filled(
                imgui.Vec2(position[0] - size, position[1] - size),
                imgui.Vec2(position[0] + size, position[1] + size),
                imgui.color_convert_float4_to_u32(0.6, .6, .6, 0.05)
            )

    def draw_brush_size(self):
        import imgui
        context = bpy.context
        size = self.get_size(context)
        color = bpy.context.preferences.themes[0].user_interface.wcol_numslider.item[:]

        with imgui.begin_group():
            start_pos = imgui.get_cursor_pos()
            imgui.set_cursor_pos(start_pos)
            imgui.push_style_color(imgui.COLOR_PLOT_HISTOGRAM, *(*color[:3], 1))
            imgui.progress_bar(size / 500, (imgui.calculate_item_width(), 20.0), overlay='R:{}'.format(size))
            imgui.pop_style_color(1)

            imgui.push_style_color(imgui.COLOR_FRAME_BACKGROUND, 1 / 7.0, 0.6, 1, 0)
            imgui.push_style_color(imgui.COLOR_FRAME_BACKGROUND_HOVERED, 1 / 7.0, .7, 1, 0)
            imgui.push_style_color(imgui.COLOR_FRAME_BACKGROUND_ACTIVE, 1.0, 1.0, 1.0, 0)
            imgui.set_cursor_pos(start_pos)

            change, size = imgui.drag_float('##Size', size, 1, 1, 500, '', imgui.SLIDER_FLAGS_NO_INPUT)
            if change:
                self.set_size(context, int(size))

            imgui.pop_style_color(3)

    def draw_brush_strength(self):
        import imgui
        strength = self.get_strength(bpy.context)

        imgui.begin_group()

        color = bpy.context.preferences.themes[0].user_interface.wcol_numslider.item[:]
        start_ops = imgui.Vec2(imgui.get_cursor_pos().x, imgui.get_cursor_pos().y)

        progress = 0.0
        progress_dir = 1.0
        progress += progress_dir * 0.4 * imgui.get_io().delta_time

        imgui.set_cursor_pos(start_ops)
        imgui.push_style_color(imgui.COLOR_PLOT_HISTOGRAM, *(*color[:3], 1))
        imgui.progress_bar(strength, (imgui.calculate_item_width(), 20.0), f'S:{strength:.3f}')
        imgui.pop_style_color(1)

        imgui.push_style_color(imgui.COLOR_FRAME_BACKGROUND, 1 / 7.0, 0.6, 1, 0)
        imgui.push_style_color(imgui.COLOR_FRAME_BACKGROUND_HOVERED, 1 / 7.0, .7, 1, 0)
        imgui.push_style_color(imgui.COLOR_FRAME_BACKGROUND_ACTIVE, 1.0, 1.0, 1.0, 0)

        imgui.set_cursor_pos(start_ops)
        chan, strength = imgui.drag_float(
            '##Strength',
            strength,
            0.005,
            0,
            1.0,
            '',
            imgui.SLIDER_FLAGS_NO_INPUT)

        imgui.pop_style_color(3)
        if chan:
            self.set_strength(bpy.context, strength)

        imgui.end_group()

    def draw_palettes(self):
        import imgui

        imgui.push_id("##draw_palettes")

        colors = list(reversed([c.color for c in self.get_palette().colors]))

        imgui.push_style_var(imgui.STYLE_FRAME_ROUNDING, 0)
        imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (1, 1))
        imgui.push_style_var(imgui.STYLE_ITEM_INNER_SPACING, (1, 1))
        imgui.push_style_var(imgui.STYLE_CHILD_BORDERSIZE, 0)
        imgui.push_style_var(imgui.STYLE_SCROLLBAR_SIZE, 2 if len(colors) > 10 else 0)

        s_size = 20

        row_count = 0
        column_count = 0

        width = imgui.calculate_item_width()
        max_line_count = int((width + 20) // (s_size + 1))  # 取商 每行能显示多少个

        with imgui.begin_child("draw _palettes",
                               width, 63.0,
                               True
                               ):
            start_pos = imgui.Vec2(imgui.get_cursor_pos().x, imgui.get_cursor_pos().y)
            self.draw_preview_color()
            imgui.set_cursor_pos(start_pos)
            imgui.columns(max_line_count, "color_list", False)

            imgui.next_column()
            row_count += 1

            for index, col in enumerate(colors):
                if max_line_count - 1 == row_count:
                    column_count += 1
                    row_count = 0

                if column_count == 1 and row_count == 0:
                    imgui.next_column()
                    imgui.next_column()
                    imgui.next_column()
                    row_count += 2
                else:
                    imgui.next_column()
                    row_count += 1
                if imgui.color_button(f'palette##{col}', *col, 1.0, s_size, s_size):
                    self.set_color(bpy.context, col, sync_to_hsv=True)
        imgui.pop_style_var(5)
        imgui.pop_id()

    def draw_preview_color(self):
        import imgui

        color = self.start_color

        start_pos = imgui.Vec2(imgui.get_cursor_pos().x, imgui.get_cursor_pos().y)
        imgui.set_cursor_pos(start_pos)
        imgui.push_style_var(imgui.STYLE_FRAME_BORDERSIZE, 0)
        imgui.push_style_var(imgui.STYLE_ITEM_INNER_SPACING, (-2, -2))
        imgui.push_style_var(imgui.STYLE_INDENT_SPACING, -2, )
        imgui.begin_group()

        s_size = 39
        changed = imgui.color_button('##current', *color, 1.0, imgui.COLOR_EDIT_NO_DRAG_DROP,
                                     s_size + 2, s_size + 1)
        if changed:
            bpy.context.window_manager.clipboard = rgb_to_hex(color)

        imgui.end_group()
        imgui.pop_style_var(3)
