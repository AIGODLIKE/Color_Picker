import math

import bpy

color_edit_active_component = None
slider_width = 256


def im_clamp(v, mn, mx):
    return max(mn, min(mx, v))


def color_edit_restore_hs(color, H, S, V):
    from imgui_bundle import imgui
    g_Gimgui = imgui.get_current_context()
    assert g_Gimgui.color_edit_current_id != 0, 'ColorEditCurrentID should not be zero'
    if (
            g_Gimgui.color_edit_saved_id != g_Gimgui.color_edit_current_id or g_Gimgui.color_edit_saved_color != imgui.color_convert_float4_to_u32(
        imgui.ImVec4(color[0], color[1], color[2], 0))):
        # print('aaaa')
        pass
    # return
    if (S == 0.0 or (H == 0.0 and g_Gimgui.color_edit_saved_hue == 1)):
        H = g_Gimgui.color_edit_saved_hue
    if V == 0.0:
        S = g_Gimgui.color_edit_saved_sat
    # print('bbb',H, S, V)
    return H, S, V


def color_edit_restore_h(color, H):
    from imgui_bundle import imgui
    g_Gimgui = imgui.get_current_context()
    assert g_Gimgui.color_edit_current_id != 0
    if g_Gimgui.color_edit_saved_id != g_Gimgui.color_edit_current_id or g_Gimgui.color_edit_saved_color != imgui.color_convert_float4_to_u32(
            imgui.ImVec4(color[0], color[1], color[2], 0)):
        return H
    # print('g_Gimgui.color_edit_saved_hue',g_Gimgui.color_edit_saved_hue)
    return g_Gimgui.color_edit_saved_hue if g_Gimgui.color_edit_saved_hue is not None else H


def get_wheeL_tri(mouse_pos):
    from imgui_bundle import imgui

    sv_picker_size = 256
    # print('三角sv_picker_size',sv_picker_size)
    # square_sz = imgui.get_frame_height()
    square_sz = 19
    # print('三角square_sz',square_sz)
    bars_width = square_sz
    region = bpy.context.region
    # print('region',region.height)
    picker_pos = imgui.ImVec2(mouse_pos[0] - 127, mouse_pos[1] + 110)
    # print('三角picker_pos', picker_pos)
    # picker_pos=imgui.get_mouse_pos()
    wheel_thickness = sv_picker_size * 0.08
    wheel_r_outer = sv_picker_size * 0.50
    wheel_r_inner = wheel_r_outer - wheel_thickness
    wheel_center = imgui.ImVec2(picker_pos.x + (sv_picker_size + bars_width) * 0.5,
                                picker_pos.y - sv_picker_size * 0.5)
    # print('三角 sv_picker_size * 0.5', sv_picker_size * 0.5)
    # print('三角wheel_center', wheel_center)
    # print('三角bars_width', bars_width)
    # print('三角sv_picker_size', sv_picker_size)

    triangle_r = wheel_r_inner - int(sv_picker_size * 0.027)
    triangle_pa = imgui.ImVec2(triangle_r, 0.0)  # Hue point.
    triangle_pc = imgui.ImVec2(triangle_r * -0.5,
                               triangle_r * -0.866025)  # White point.-0.5 和 -0.866025 分别是 cos(120°) 和 sin(120°) 的值。
    triangle_pb = imgui.ImVec2(triangle_r * -0.5, triangle_r * +0.866025)
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
    # return (wheel_center.x,wheel_center.y),tra, trb, trc
    return list


class ColorWidget:

    def draw_color_picker_wheel(self):
        from imgui_bundle import imgui

        # item_flags = imgui.internal.ItemFlags_
        color_flags = imgui.ColorEditFlags_

        print(imgui.is_window_focused())


        # 拾取器 上下文
        gc = imgui.get_current_context()
        window = imgui.internal.get_current_window()

        draw_list = imgui.get_window_draw_list()
        style = gc.style
        io = gc.io

        # 检查各种标志
        width = imgui.calc_item_width()

        # is_readonly = ((gc.next_item_data.item_flags | gc.current_item_flags) & item_flags.read_only) != 0

        # 唯一标识符
        imgui.push_id(self.bl_idname + "draw_color_picker_wheel")
        imgui.begin_group()

        set_current_color_edit_id = (gc.color_edit_current_id == 0)
        # 当前窗口的顶部ID将作为当前颜色编辑器的ID

        if set_current_color_edit_id:
            gc.color_edit_current_id = window.id_stack.__getitem__(window.id_stack.size() - 1)

        # if not (color_flags & color_flags):
        #     color_flags |= imgui.COLOR_EDIT_NO_SIDE_PREVIEW
        # if not (color_flags & imgui.COLOR_EDIT_NO_OPTIONS):
        #     imgui.internal.color_picker_options_popup(color, color_flags)
        #
        # if not (color_flags & color_flags.picker_mask_):
        #     if gc.color_edit_options & color_flags.picker_mask_:
        #         color_flags |= gc.color_edit_options & color_flags.picker_mask_
        #     else:
        #         color_flags |= color_flags.default_options_ & color_flags.picker_mask
        # if not (color_flags & color_flags.input_mask_):
        #     if gc.color_edit_options & color_flags.input_mask_:
        #         color_flags |= gc.color_edit_options & color_flags.input_mask_
        #     else:
        #         imgui.ColorEditFlags_.default_options_ & color_flags.input_mask_
        # assert imgui.internal.im_is_power_of_two(color_flags & color_flags.picker_mask_)
        # assert imgui.internal.im_is_power_of_two(color_flags & color_flags.input_mask_)
        # if not (color_flags & imgui.ColorEditFlags_.no_options):
        #     color_flags |= gc.color_edit_options & color_flags.alpha_bar

        # 设置
        # components = 3 if color_flags & imgui.ColorEditFlags_.no_alpha else 4
        # alpha_bar = (color_flags & color_flags.alpha_bar) and (
        #     not (color_flags & color_flags.no_alpha))
        alpha_bar = True
        picker_pos = imgui.ImVec2(window.dc.cursor_pos.x, window.dc.cursor_pos.y)
        picker_pos2 = imgui.get_cursor_pos()
        # picker_pos = imgui.get_window_pos()

        square_sz = imgui.get_frame_height()

        bars_width = square_sz

        sv_picker_size = max(bars_width * 1,
                             width - (bars_width + style.item_inner_spacing.x))  # Saturation / Value picking box
        sv_picker_size = max(bars_width * 1, 256)  # Saturation / Value picking box
        bar0_pos_x = picker_pos.x + sv_picker_size + style.item_inner_spacing.x
        # print('bar0_pos_x',bar0_pos_x)
        bar1_pos_x = bar0_pos_x + bars_width + style.item_inner_spacing.x
        bars_triangles_half_sz = imgui.internal.im_trunc(bars_width * 0.20)

        wheel_thickness = sv_picker_size * 0.08
        wheel_r_outer = sv_picker_size * 0.50
        wheel_r_inner = wheel_r_outer - wheel_thickness
        wheel_center = imgui.ImVec2(picker_pos.x + (sv_picker_size + bars_width) * 0.5,
                                    picker_pos.y + sv_picker_size * 0.5)
        # 该三角形被显示为旋转状态, 其中triangle_pa指向色调(Hue)
        # 方向, 但大部分坐标仍保持未旋转, 用于逻辑计算。
        triangle_r = wheel_r_inner - int(sv_picker_size * 0.027)
        triangle_pa = imgui.ImVec2(triangle_r, 0.0)  # Hue point.
        triangle_pc = imgui.ImVec2(triangle_r * -0.5,
                                   triangle_r * -0.866025)  # White point.-0.5 和 -0.866025 分别是 cos(120°) 和 sin(120°) 的值。
        triangle_pb = imgui.ImVec2(triangle_r * -0.5,
                                   triangle_r * +0.866025)  # Black  point.-0.5 和 0.866025 分别是 cos(240°) 和 sin(240°) 的值
        sqrt2 = 1.4142135
        quad_size = 2 * triangle_r / sqrt2
        offset_l_up = imgui.ImVec2(triangle_r / -sqrt2, triangle_r / -sqrt2)
        offset_r_bot = imgui.ImVec2(triangle_r / sqrt2, triangle_r / sqrt2)
        # print(triangle_pc.y,triangle_pb.y)
        # print(triangle_pc.y-triangle_pb.y)
        color = self.start_color
        H = color.hsv[0]
        S = color.hsv[1]
        V = color.hsv[2]
        R = color[0]
        G = color[1]
        B = color[2]
        # print('imgui picker_pos3111222', picker_pos)
        input_rgb = True
        # if color_flags & imgui.ColorEditFlags_.input_rgb:
        if input_rgb:
            H, S, V = imgui.color_convert_rgb_to_hsv(R, G, B, H, S, V)
            # print('11', H, S, V)
            H, S, V = color_edit_restore_hs(color.hsv, H, S, V)
            # print('22', H, S, V)
        # elif color_flags & imgui.ColorEditFlags_.input_hsv:
        #     R, G, B = imgui.color_convert_hsv_to_rgb(H, S, V, R, G, B)
        # print('33', R, G, B)
        # 初始化变量，用于跟踪颜色值的变化
        value_changed = False
        value_changed_h = False
        value_changed_sv = False
        # 设置当前UI元素不响应键盘导航，以免影响色相选择
        imgui.push_item_flag(imgui.ItemFlags_.no_nav, True)
        global color_edit_active_component
        # 如果设置了色相环选择标志，则执行色相环和SV三角形的逻辑
        picker_hue_wheel = True
        picker_hue_bar = False
        if picker_hue_wheel:
            imgui.invisible_button('hsv', imgui.ImVec2(sv_picker_size + style.item_inner_spacing.x + bars_width,
                                                       sv_picker_size))
            # print('activce', imgui.is_item_active(), 'read ', is_readonly)
            # 全局变量用于跟踪当前激活的控件

            # 检查是否需要更新当前激活的控件
            if imgui.is_item_active() and color_edit_active_component is None:
                initial_off = imgui.ImVec2(gc.io.mouse_pos_prev.x - wheel_center.x,
                                           gc.io.mouse_pos_prev.y - wheel_center.y)
                initial_dist2 = imgui.internal.im_length_sqr(initial_off)
                if imgui.internal.im_triangle_contains_point(triangle_pa, triangle_pb, triangle_pc, initial_off):
                    color_edit_active_component = 'triangle'
                elif initial_dist2 >= ((wheel_r_inner - 1) * (wheel_r_inner - 1)) and initial_dist2 <= (
                        (wheel_r_outer + 1) * (wheel_r_outer + 1)):
                    color_edit_active_component = 'wheel'

            # 检查当前激活的控件并更新颜色值
            if color_edit_active_component == 'triangle':
                current_off_unrotated = imgui.ImVec2(gc.io.mouse_pos.x - wheel_center.x,
                                                     gc.io.mouse_pos.y - wheel_center.y)
                if not imgui.internal.im_triangle_contains_point(triangle_pa, triangle_pb, triangle_pc,
                                                                 current_off_unrotated):
                    current_off_unrotated = imgui.internal.im_triangle_closest_point(triangle_pa, triangle_pb,
                                                                                     triangle_pc,
                                                                                     current_off_unrotated)

                uu, vv, ww = 0.0, 0.0, 0.0
                uu, vv, ww = imgui.internal.im_triangle_barycentric_coords(triangle_pa, triangle_pb, triangle_pc,
                                                                           current_off_unrotated, uu, vv, ww)
                V = im_clamp(1.0 - vv, 0.0001, 1.0)
                S = im_clamp(uu / V, 0.0001, 1.0)
                value_changed = value_changed_sv = True

            elif color_edit_active_component == 'wheel':
                current_off = imgui.ImVec2(gc.io.mouse_pos.x - wheel_center.x, gc.io.mouse_pos.y - wheel_center.y)
                H = math.atan2(current_off.y, current_off.x) / math.pi * 0.5
                if H < .0:
                    H += 1.0
                value_changed = value_changed_h = True

            # 重置激活的控件状态
            if not imgui.is_item_active():
                color_edit_active_component = None
            #     if imgui.internal.im_triangle_contains_point(triangle_pa, triangle_pb, triangle_pc, imgui.internal.im_rotate(initial_off,cos_hue_angle,sin_hue_angle)):
            #         current_off_unrotated=imgui.internal.im_rotate(current_off, cos_hue_angle, sin_hue_angle)
            #         if not imgui.internal.im_triangle_contains_point(triangle_pa, triangle_pb, triangle_pc, current_off_unrotated):
            #             current_off_unrotated=imgui.internal.im_triangle_closest_point(triangle_pa, triangle_pb, triangle_pc, current_off_unrotated)
            #         uu,vv,ww=.0,.0,.0
            #         uu, vv, ww=imgui.internal.im_triangle_barycentric_coords(triangle_pa, triangle_pb, triangle_pc, current_off_unrotated, uu, vv, ww)
            #         V=im_clamp(1.0-vv,0.0001,1.0)
            #         S=im_clamp(uu/V,0.0001,1.0)
            #         value_changed = value_changed_sv = True
            # if not (color_flags & imgui.ColorEditFlags_.no_options):
            #     imgui.open_popup_on_item_click('context', imgui.PopupFlags_.mouse_button_right)
        elif picker_hue_bar:
            imgui.invisible_button('hsv', imgui.ImVec2(sv_picker_size + style.item_inner_spacing.x + bars_width,
                                                       sv_picker_size))
            # 检查是否需要更新当前激活的控件
            if imgui.is_item_active() and color_edit_active_component is None:
                initial_off = imgui.ImVec2(gc.io.mouse_pos_prev.x - wheel_center.x,
                                           gc.io.mouse_pos_prev.y - wheel_center.y)
                initial_dist2 = imgui.internal.im_length_sqr(initial_off)
                quad_l_up = imgui.ImVec2(wheel_center.x + offset_l_up.x, wheel_center.y + offset_l_up.y)
                quad_r_bot = imgui.ImVec2(wheel_center.x + offset_r_bot.x, wheel_center.y + offset_r_bot.y)

                if (quad_l_up.x <= io.mouse_pos.x <= quad_r_bot.x and
                        quad_l_up.y <= io.mouse_pos.y <= quad_r_bot.y):
                    color_edit_active_component = 'square'
                if initial_dist2 >= ((wheel_r_inner - 1) * (wheel_r_inner - 1)) and initial_dist2 <= (
                        (wheel_r_outer + 1) * (wheel_r_outer + 1)):
                    color_edit_active_component = 'wheel'

            # 检查当前激活的控件并更新颜色值
            if color_edit_active_component == 'square':
                l_up = imgui.ImVec2(wheel_center.x + offset_l_up.x, wheel_center.y + offset_l_up.y)
                S = imgui.internal.im_saturate((io.mouse_pos.x - l_up.x) / (quad_size - 1))
                V = 1.0 - imgui.internal.im_saturate((io.mouse_pos.y - l_up.y) / (quad_size - 1))
                # print(H)
                H = color_edit_restore_h(color, H)
                # print('H=color_edit_restore_h(color,H)',H)
                # H,S,V=color_edit_restore_hs(color,H,S,V)
                value_changed = value_changed_sv = True

            elif color_edit_active_component == 'wheel':
                current_off = imgui.ImVec2(gc.io.mouse_pos.x - wheel_center.x, gc.io.mouse_pos.y - wheel_center.y)
                H = math.atan2(current_off.y, current_off.x) / math.pi * 0.5
                if H < .0:
                    H += 1.0
                # print('wheel',H)
                value_changed = value_changed_h = True
                # 重置激活的控件状态
            if not imgui.is_item_active():
                color_edit_active_component = None
            # print('imgui picker_p12322113', picker_pos)
            imgui.set_cursor_screen_pos(imgui.ImVec2(bar0_pos_x, picker_pos.y))
            # print('imgui picker_pos231311113', picker_pos)
            # imgui.invisible_button("hue", imgui.ImVec2(bars_width, sv_picker_size))

        if alpha_bar:
            pass
        imgui.pop_item_flag()
        if value_changed_h or value_changed_sv:
            if input_rgb:

                color[0], color[1], color[2] = imgui.color_convert_hsv_to_rgb(H, S, V, color[0], color[1], color[2])
                gc.color_edit_saved_hue = H
                gc.color_edit_saved_sat = S
                gc.color_edit_saved_id = gc.color_edit_current_id
                gc.color_edit_saved_color = imgui.color_convert_float4_to_u32(
                    imgui.ImVec4(color[0], color[1], color[2], 0.0))
            elif color_flags & imgui.ColorEditFlags_.input_hsv:
                color.h = H
                color.s = S
                color.v = V
        value_changed_fix_hue_wrap = False
        if value_changed_fix_hue_wrap and (input_rgb):
            new_H, new_S, new_V = .0, .0, .0
            new_H, new_S, new_V = imgui.color_convert_rgb_to_hsv(color.h, color.s, color.v, new_H, new_S, new_V)
            if new_H <= .0 and H > .0:
                pass
                if new_V <= 0 and V != new_V:
                    color[0], color[1], color[2] = imgui.color_convert_hsv_to_rgb(H, S,
                                                                                  V * 0.5 if new_V <= 0 else new_V,
                                                                                  color[0], color[1], color[2])
                    color.hsv = (H, S, V)
                elif new_S <= 0:
                    color[0], color[1], color[2] = imgui.color_convert_hsv_to_rgb(H, S * 0.5 if new_S <= 0 else new_S,
                                                                                  color[0], color[1], color[2])
                    color.hsv = (H, S, V)
        if value_changed:
            if input_rgb:
                R = color[0]
                G = color[1]
                B = color[2]
                H, S, V = imgui.color_convert_rgb_to_hsv(R, G, B, H, S, V)
                H, S, V = color_edit_restore_hs(color, H, S, V)
            elif color_flags & imgui.ColorEditFlags_.input_hsv:
                H = color.h
                S = color.s
                V = color.v
                R, G, B = imgui.color_convert_hsv_to_rgb(H, S, V, R, G, B)

        col_black = imgui.color_convert_float4_to_u32(imgui.ImVec4(0.0, 0.0, 0.0, 1.0))
        col_white = imgui.color_convert_float4_to_u32(imgui.ImVec4(1.0, 1.0, 1.0, 1.0))
        col_midgrey = imgui.color_convert_float4_to_u32(imgui.ImVec4(0.5, 0.5, 0.5, 0.0))
        col_hues = [
            imgui.get_color_u32(imgui.ImVec4(255, 0, 0, 255)),  # 红色
            imgui.get_color_u32(imgui.ImVec4(255, 255, 0, 255)),  # 黄色
            imgui.get_color_u32(imgui.ImVec4(0, 255, 0, 255)),  # 绿色
            imgui.get_color_u32(imgui.ImVec4(0, 255, 255, 255)),  # 青色
            imgui.get_color_u32(imgui.ImVec4(0, 0, 255, 255)),  # 蓝色
            imgui.get_color_u32(imgui.ImVec4(255, 0, 255, 255)),  # 品红
            imgui.get_color_u32(imgui.ImVec4(255, 0, 0, 255))  # 红色(再次出现以闭合色环)
        ]

        hue_color_f = imgui.ImVec4(1, 1, 1, 1)
        # print('hue_color_f',hue_color_f)
        hue_color_f = imgui.ImVec4(
            *(imgui.color_convert_hsv_to_rgb(H, 1, 1, hue_color_f.x, hue_color_f.y, hue_color_f.z)),
            1)

        # print('hue_color_f2', hue_color_f)
        hue_color32 = imgui.color_convert_float4_to_u32(hue_color_f)
        user_col32_striped_of_alpha = imgui.color_convert_float4_to_u32(
            imgui.ImVec4(R, G, B, 1))  # Important: this is still including the main rendering / style alpha!!

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
            gradient_p0 = imgui.ImVec2(wheel_center.x + math.cos(a0) * wheel_r_inner,
                                       wheel_center.y + math.sin(a0) * wheel_r_inner)  # 起始点的坐标
            gradient_p1 = imgui.ImVec2(wheel_center.x + math.cos(a1) * wheel_r_inner,
                                       wheel_center.y + math.sin(a1) * wheel_r_inner)  # 结束点的坐标
            imgui.internal.shade_verts_linear_color_gradient_keep_alpha(imgui.get_window_draw_list(), vert_start_idx,
                                                                        vert_end_idx, gradient_p0, gradient_p1,
                                                                        col_hues[n], col_hues[n + 1])
        cos_hue_angle = math.cos(H * 2.0 * math.pi)
        sin_hue_angle = math.sin(H * 2.0 * math.pi)
        hue_cursor_pos = imgui.ImVec2(wheel_center.x + cos_hue_angle * (wheel_r_inner + wheel_r_outer) * 0.5,
                                      wheel_center.y + sin_hue_angle * (wheel_r_inner + wheel_r_outer) * 0.5)

        hue_cursor_rad = wheel_thickness * 0.65 if value_changed_h else wheel_thickness * 0.55
        # print('hue_cursor_rad', hue_cursor_rad)
        # hue_cursor_rad = 5.0
        hue_cursor_segments = imgui.get_window_draw_list()._calc_circle_auto_segment_count(hue_cursor_rad)
        imgui.get_window_draw_list().add_circle_filled(hue_cursor_pos, hue_cursor_rad, hue_color32, hue_cursor_segments)
        imgui.get_window_draw_list().add_circle(hue_cursor_pos, hue_cursor_rad + 1, col_midgrey, hue_cursor_segments)
        imgui.get_window_draw_list().add_circle(hue_cursor_pos, hue_cursor_rad, col_white, hue_cursor_segments)

        # 圆环上的 按钮
        # if color_flags & imgui.ColorEditFlags_.picker_hue_wheel:
        if picker_hue_wheel:
            tra = imgui.ImVec2((wheel_center.x + triangle_pa.x), (wheel_center.y + triangle_pa.y))
            trb = imgui.ImVec2((wheel_center.x + triangle_pb.x), (wheel_center.y + triangle_pb.y))
            trc = imgui.ImVec2((wheel_center.x + triangle_pc.x), (wheel_center.y + triangle_pc.y))
            uv_white = imgui.get_font_tex_uv_white_pixel()

            imgui.get_window_draw_list().prim_reserve(3, 3)
            imgui.get_window_draw_list().prim_vtx(tra, uv_white, hue_color32)
            imgui.get_window_draw_list().prim_vtx(trb, uv_white, col_black)
            imgui.get_window_draw_list().prim_vtx(trc, uv_white, col_white)
            imgui.get_window_draw_list().add_triangle(tra, trb, trc, col_midgrey, 0)
            sv_cursor_pos = imgui.internal.im_lerp(imgui.internal.im_lerp(trc, tra, imgui.internal.im_saturate(S)), trb,
                                                   imgui.internal.im_saturate(1 - V))
        # 绘制正方形
        # elif color_flags & imgui.ColorEditFlags_.picker_hue_bar:
        elif picker_hue_bar:
            # print('imgui picker_pos2', picker_pos)
            l_up = imgui.ImVec2(wheel_center.x + offset_l_up.x, wheel_center.y + offset_l_up.y)
            r_bot = imgui.ImVec2(wheel_center.x + offset_r_bot.x, wheel_center.y + offset_r_bot.y)

            draw_list.add_rect_filled_multi_color(l_up, r_bot, col_white, hue_color32, hue_color32, col_white)
            draw_list.add_rect_filled_multi_color(l_up, r_bot, 0, 0, col_black, col_black)
            imgui.internal.render_frame_border(l_up, r_bot, 0.0)
            # 彩色bar
            sv_cursor_pos = imgui.ImVec2(0, 0)
            sv_cursor_pos.x = im_clamp(round((l_up).x + imgui.internal.im_saturate(S) * quad_size), (l_up).x + 2,
                                       picker_pos.x + sv_picker_size - 2)
            sv_cursor_pos.y = im_clamp(round((l_up).y + imgui.internal.im_saturate(1 - V) * quad_size), (l_up).y + 2,
                                       (l_up).y + quad_size - 2)
        sv_cursor_rad = wheel_thickness * 0.55 if value_changed_sv else wheel_thickness * 0.4
        sv_cursor_segments = imgui.get_window_draw_list()._calc_circle_auto_segment_count(sv_cursor_rad)
        # 游标颜色
        imgui.get_window_draw_list().add_circle_filled(sv_cursor_pos, sv_cursor_rad, user_col32_striped_of_alpha,
                                                       sv_cursor_segments)
        imgui.get_window_draw_list().add_circle(sv_cursor_pos, sv_cursor_rad + 1, col_midgrey, sv_cursor_segments)
        imgui.get_window_draw_list().add_circle(sv_cursor_pos, sv_cursor_rad, col_white, sv_cursor_segments)
        # ops.sv_cursor_pos = sv_cursor_pos
        # ops.sv_cursor_rad = sv_cursor_rad
        imgui.end_group()
        if value_changed and gc.last_item_data.id_ != 0:
            imgui.internal.mark_item_edited(gc.last_item_data.id_)
        if set_current_color_edit_id:
            gc.color_edit_current_id = 0
        imgui.pop_id()
        # ops.h = H
        # ops.s = S
        # ops.v = V
        return value_changed, picker_pos, picker_pos2, wheel_center

    def draw_color_picker_bar(self):
        ...
