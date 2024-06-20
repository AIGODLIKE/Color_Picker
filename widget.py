import math
import numpy as np
from .extern.imgui_bundle import imgui

def im_clamp(v, mn, mx):
    return max(mn, min(mx, v))
def color_edit_restore_hs(color, H, S, V):
    g_Gimgui = imgui.get_current_context()
    assert g_Gimgui.color_edit_current_id != 0, 'ColorEditCurrentID should not be zero'
    if (
            g_Gimgui.color_edit_saved_id != g_Gimgui.color_edit_current_id or g_Gimgui.color_edit_saved_color != imgui.color_convert_float4_to_u32(
        imgui.ImVec4(color[0], color[1], color[2], 0))):
        return H, S, V
    if (S == 0.0 or (H == 0.0 and g_Gimgui.color_edit_saved_hue == 1)):
        H = g_Gimgui.color_edit_saved_hue
    if V == 0.0:
        S = g_Gimgui.color_edit_saved_sat
    return H, S, V

def colorpicker(label, color, flags, ref_col=None):
    # 拾取器 上下文
    g_Gimgui = imgui.get_current_context()
    window = imgui.internal.get_current_window()
    if window.skip_items:
        return False
    draw_list = window.draw_list
    style = g_Gimgui.style
    io = g_Gimgui.io

    # 检查各种标志
    width = imgui.calc_item_width()

    is_readonly = ((
                           g_Gimgui.next_item_data.item_flags | g_Gimgui.current_item_flags) & imgui.internal.ItemFlags_.read_only) != 0
    g_Gimgui.next_item_data.clear_flags()
    # 唯一标识符
    imgui.push_id('hsv_picker')

    set_current_color_edit_id = (g_Gimgui.color_edit_current_id == 0)
    # 当前窗口的顶部ID将作为当前颜色编辑器的ID
    if set_current_color_edit_id:
        g_Gimgui.color_edit_current_id = window.id_stack.__getitem__(window.id_stack.size() - 1)
    imgui.begin_group()

    if not (flags & imgui.ColorEditFlags_.no_side_preview):
        flags |= imgui.ColorEditFlags_.no_side_preview
    if not (flags & imgui.ColorEditFlags_.no_options):
        imgui.internal.color_picker_options_popup(color, flags)

    if not (flags & imgui.ColorEditFlags_.picker_mask_):
        if g_Gimgui.color_edit_options & imgui.ColorEditFlags_.picker_mask_:
            flags |= g_Gimgui.color_edit_options & imgui.ColorEditFlags_.picker_mask_
        else:
            flags |= imgui.ColorEditFlags_.default_options_ & imgui.ColorEditFlags_.picker_mask
    if not (flags & imgui.ColorEditFlags_.input_mask_):
        if g_Gimgui.color_edit_options & imgui.ColorEditFlags_.input_mask_:
            flags |= g_Gimgui.color_edit_options & imgui.ColorEditFlags_.input_mask_
        else:
            imgui.ColorEditFlags_.default_options_ & imgui.ColorEditFlags_.input_mask_
    assert imgui.internal.im_is_power_of_two(flags & imgui.ColorEditFlags_.picker_mask_)
    assert imgui.internal.im_is_power_of_two(flags & imgui.ColorEditFlags_.input_mask_)
    if not (flags & imgui.ColorEditFlags_.no_options):
        flags |= g_Gimgui.color_edit_options & imgui.ColorEditFlags_.alpha_bar

    # 设置
    components = 3 if flags & imgui.ColorEditFlags_.no_alpha else 4
    alpha_bar = (flags & imgui.ColorEditFlags_.alpha_bar) and (not (flags & imgui.ColorEditFlags_.no_alpha))
    picker_pos = window.dc.cursor_pos
    square_sz = imgui.get_frame_height()
    bars_width = square_sz

    # sv_picker_size = max(bars_width * 1, width - (
    #         bars_width + imgui.get_style().item_inner_spacing.x))  # Saturation / Value picking box
    sv_picker_size = max(bars_width * 1, 256)  # Saturation / Value picking box
    # print('widthwidth', bars_width + imgui.get_style().item_inner_spacing.x)
    bar0_pos_x = picker_pos.x + sv_picker_size + style.item_inner_spacing.x
    bar1_pos_x = bar0_pos_x + bars_width + style.item_inner_spacing.x
    bars_triangles_half_sz = imgui.internal.im_trunc(bars_width * 0.20)

    backup_initial_col = color[:components]

    wheel_thickness = sv_picker_size * 0.08
    wheel_r_outer = sv_picker_size * 0.50
    wheel_r_inner = wheel_r_outer - wheel_thickness
    wheel_center = imgui.ImVec2(picker_pos.x + (sv_picker_size + bars_width) * 0.5,
                                picker_pos.y + sv_picker_size * 0.5)
    # 该三角形被显示为旋转状态, 其中triangle_pa指向色调(Hue)
    # 方向, 但大部分坐标仍保持未旋转, 用于逻辑计算。
    triangle_r = wheel_r_inner - int(sv_picker_size * 0.027)
    triangle_pa = imgui.ImVec2(triangle_r, 0.0)  # Hue point.
    triangle_pc = imgui.ImVec2(triangle_r * -0.5, triangle_r * -0.866025)  #  White point.
    triangle_pb = imgui.ImVec2(triangle_r * -0.5, triangle_r * +0.866025)  #Black  point.

    H = color[0]
    S = color[1]
    V = color[2]
    R = color[0]
    G = color[1]
    B = color[2]

    if flags & imgui.ColorEditFlags_.input_rgb:
        H, S, V=imgui.color_convert_rgb_to_hsv(R, G, B, H, S, V)
        H,S,V=color_edit_restore_hs(color, H, S, V)
    elif flags & imgui.ColorEditFlags_.input_hsv:
        R, G, B=imgui.color_convert_hsv_to_rgb(H, S, V, R, G, B)
    # 初始化变量，用于跟踪颜色值的变化
    value_changed = False
    value_changed_h = False
    value_changed_sv = False
    # 设置当前UI元素不响应键盘导航，以免影响色相选择
    imgui.internal.push_item_flag(imgui.internal.ItemFlags_.no_nav, True)
    # // 如果设置了色相环选择标志，则执行色相环和SV三角形的逻辑
    if flags & imgui.ColorEditFlags_.picker_hue_wheel:
        imgui.invisible_button('hsv', imgui.ImVec2(sv_picker_size + style.item_inner_spacing.x + bars_width,
                                                   sv_picker_size))
        print('activce',imgui.is_item_active(),'read ',is_readonly)
        if imgui.is_item_active() and (not is_readonly):
            print('',imgui.is_item_active() and (not is_readonly))
            initial_off = g_Gimgui.io.mouse_pos_prev - wheel_center

            current_off = g_Gimgui.io.mouse_pos - wheel_center
            initial_dist2 = imgui.internal.im_length_sqr(initial_off)
            if ((initial_dist2 >= ((wheel_r_inner - 1) * (wheel_r_inner - 1))) and (initial_dist2 <= ((wheel_r_outer + 1) * (
                    wheel_r_outer + 1)))):
                H = math.atan2(current_off.y, current_off.x) / math.pi * 0.5
                if H < .0:
                    H += 1.0
                value_changed = value_changed_h = True
            cos_hue_angle = math.cos(-H * 2.0 * math.pi)
            sin_hue_angle = math.sin(-H * 2.0 * math.pi)
            #三角形
            if imgui.internal.im_triangle_contains_point(triangle_pa, triangle_pb, triangle_pc, initial_off):
                current_off_unrotated=current_off
                if not imgui.internal.im_triangle_contains_point(triangle_pa, triangle_pb, triangle_pc, current_off_unrotated):
                    current_off_unrotated=imgui.internal.im_triangle_closest_point(triangle_pa, triangle_pb, triangle_pc, current_off_unrotated)
                uu,vv,ww=.0,.0,.0
                uu, vv, ww=imgui.internal.im_triangle_barycentric_coords(triangle_pa, triangle_pb, triangle_pc, current_off_unrotated, uu, vv, ww)
                V=im_clamp(1.0-vv,0.0001,1.0)
                S=im_clamp(uu/V,0.0001,1.0)
                value_changed = value_changed_sv = True
            # if imgui.internal.im_triangle_contains_point(triangle_pa, triangle_pb, triangle_pc, imgui.internal.im_rotate(initial_off,cos_hue_angle,sin_hue_angle)):
            #     current_off_unrotated=imgui.internal.im_rotate(current_off, cos_hue_angle, sin_hue_angle)
            #     if not imgui.internal.im_triangle_contains_point(triangle_pa, triangle_pb, triangle_pc, current_off_unrotated):
            #         current_off_unrotated=imgui.internal.im_triangle_closest_point(triangle_pa, triangle_pb, triangle_pc, current_off_unrotated)
            #     uu,vv,ww=.0,.0,.0
            #     uu, vv, ww=imgui.internal.im_triangle_barycentric_coords(triangle_pa, triangle_pb, triangle_pc, current_off_unrotated, uu, vv, ww)
            #     V=im_clamp(1.0-vv,0.0001,1.0)
            #     S=im_clamp(uu/V,0.0001,1.0)
            #     value_changed = value_changed_sv = True
        # if not (flags & imgui.ColorEditFlags_.no_options):
        #     imgui.open_popup_on_item_click('context', imgui.PopupFlags_.mouse_button_right)
    if alpha_bar:
        pass
    imgui.internal.pop_item_flag()

    if not (flags & imgui.ColorEditFlags_.no_side_preview):
        imgui.same_line(0, style.item_inner_spacing.x)
        imgui.begin_group()

    if not (flags & imgui.ColorEditFlags_.no_label):
        label_display_end = imgui.internal.find_rendered_text_end(label)
        if label != label_display_end:
            if flags & imgui.ColorEditFlags_.no_side_preview:
                imgui.same_line(0, style.item_inner_spacing.x)
            imgui.internal.text_ex(label, label_display_end)

    if not (flags & imgui.ColorEditFlags_.no_side_preview):
        imgui.internal.push_item_flag(imgui.internal.ItemFlags_.no_nav_default_focus, True)
        if flags & imgui.ColorEditFlags_.no_alpha:
            col_v4 = imgui.ImVec4(color[0], color[1], color[2], 1.0)
        else:
            col_v4 = imgui.ImVec4(color[0], color[1], color[2], color[3])
        if flags & imgui.ColorEditFlags_.no_label:
            pass
        flag = imgui.ColorEditFlags_
        sub_flags_to_forward = flag.input_mask_ | flag.hdr | flag.alpha_preview | flag.alpha_preview_half | flag.no_tooltip
        imgui.color_button("##current", col_v4, (flags & sub_flags_to_forward),
                           imgui.ImVec2(square_sz * 3, square_sz * 2))
        imgui.internal.pop_item_flag()
        imgui.end_group()

    # // Convert back color to RGB
    if value_changed_h or value_changed_sv:
        if flags & imgui.ColorEditFlags_.input_rgb:

            color[0], color[1], color[2]=imgui.color_convert_hsv_to_rgb(H, S, V, color[0], color[1], color[2])

            g_Gimgui.color_edit_saved_hue = H
            g_Gimgui.color_edit_saved_sat = S
            g_Gimgui.color_edit_saved_id = g_Gimgui.color_edit_current_id
            g_Gimgui.color_edit_saved_color = imgui.color_convert_float4_to_u32(
                imgui.ImVec4(color[0], color[1], color[2], 0.0))
        elif flags & imgui.ColorEditFlags_.input_hsv:
            color[0] = H
            color[1] = S
            color[2] = V
    value_changed_fix_hue_wrap = False
    # if (flags & imgui.ColorEditFlags_.no_inputs)==0:
    if value_changed_fix_hue_wrap and (flags & imgui.ColorEditFlags_.input_rgb):
        new_H, new_S, new_V = .0, .0, .0
        new_H, new_S, new_V=imgui.color_convert_rgb_to_hsv(color[0], color[1], color[2], new_H, new_S, new_V)
        if new_H<=.0 and H>.0:

            if new_V<=0 and V!=new_V:
                color[0],color[1],color[2]=imgui.color_convert_hsv_to_rgb(H,S,V*0.5 if new_V<=0 else new_V,color[0],color[1],color[2])
            elif new_S<=0:
                color[0],color[1],color[2]=imgui.color_convert_hsv_to_rgb(H,S*0.5 if new_S<=0 else new_S,color[0],color[1],color[2])

    if value_changed:
        if flags & imgui.ColorEditFlags_.input_rgb:
            R = color[0]
            G = color[1]
            B = color[2]
            imgui.color_convert_rgb_to_hsv(R, G, B, H, S, V)
            H,S,V=color_edit_restore_hs(color, H, S, V)
        elif flags & imgui.ColorEditFlags_.input_hsv:
            H = color[0]
            S = color[1]
            V = color[2]
            imgui.color_convert_hsv_to_rgb(H, S, V, R, G, B)

    col_black = imgui.get_color_u32(imgui.ImVec4(0, 0, 0, 255))
    col_white = imgui.get_color_u32(imgui.ImVec4(255, 255, 255, 255))
    col_midgrey = imgui.get_color_u32(imgui.ImVec4(128, 128, 128, 255))
    col_hues = [
        imgui.get_color_u32(imgui.ImVec4(255, 0, 0, 255)),  # 红色
        imgui.get_color_u32(imgui.ImVec4(255, 255, 0, 255)),  # 黄色
        imgui.get_color_u32(imgui.ImVec4(0, 255, 0, 255)),  # 绿色
        imgui.get_color_u32(imgui.ImVec4(0, 255, 255, 255)),  # 青色
        imgui.get_color_u32(imgui.ImVec4(0, 0, 255, 255)),  # 蓝色
        imgui.get_color_u32(imgui.ImVec4(255, 0, 255, 255)),  # 品红
        imgui.get_color_u32(imgui.ImVec4(255, 0, 0, 255))  # 红色(再次出现以闭合色环)
    ]

    hue_color_f = imgui.ImVec4(1, 1, 1, style.alpha)
    # print('hue_color_f',hue_color_f)
    hue_color_f = imgui.ImVec4(*(imgui.color_convert_hsv_to_rgb(H, 1, 1, hue_color_f.x, hue_color_f.y, hue_color_f.z)),1)
    # print('hue_color_f2', hue_color_f)
    hue_color32 = imgui.color_convert_float4_to_u32(hue_color_f)
    user_col32_striped_of_alpha = imgui.color_convert_float4_to_u32(
        imgui.ImVec4(R, G, B, style.alpha))  # Important: this is still including the main rendering / style alpha!!

    # 圆环上的 按钮
    if flags & imgui.ColorEditFlags_.picker_hue_wheel:

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
        # imgui.pop_id()

        tra = wheel_center + imgui.internal.im_rotate(triangle_pa, cos_hue_angle, sin_hue_angle)
        trb = wheel_center + imgui.internal.im_rotate(triangle_pb, cos_hue_angle, sin_hue_angle)
        trc = wheel_center + imgui.internal.im_rotate(triangle_pc, cos_hue_angle, sin_hue_angle)

        tra = wheel_center + triangle_pa
        trb = wheel_center + triangle_pb
        trc = wheel_center + triangle_pc
        uv_white = imgui.get_font_tex_uv_white_pixel()

        imgui.get_window_draw_list().prim_reserve(3,3)
        imgui.get_window_draw_list().prim_vtx(tra, uv_white, hue_color32)
        imgui.get_window_draw_list().prim_vtx(trb, uv_white, col_black)
        imgui.get_window_draw_list().prim_vtx(trc, uv_white, col_white)
        imgui.get_window_draw_list().add_triangle(tra, trb, trc, col_midgrey, 0)
        sv_cursor_pos = imgui.internal.im_lerp(imgui.internal.im_lerp(trc, tra, imgui.internal.im_saturate(S)), trb,
                                               imgui.internal.im_saturate(1 - V))
    sv_cursor_rad=wheel_thickness*0.55 if value_changed_sv else wheel_thickness*0.4
    sv_cursor_segments=imgui.get_window_draw_list()._calc_circle_auto_segment_count(sv_cursor_rad)
    imgui.get_window_draw_list().add_circle_filled(sv_cursor_pos, sv_cursor_rad, user_col32_striped_of_alpha, sv_cursor_segments)
    imgui.get_window_draw_list().add_circle(sv_cursor_pos, sv_cursor_rad + 1, col_midgrey, sv_cursor_segments)
    imgui.get_window_draw_list().add_circle(sv_cursor_pos, sv_cursor_rad, col_white, sv_cursor_segments)
    imgui.end_group()
    # if value_changed and
    if set_current_color_edit_id:
        g_Gimgui.color_edit_current_id=0
    imgui.pop_id()

    # print('backup_initial_col', R,G,B)
    # a=1.0
    # b=1.0
    # c=1.0
    # imgui.color_convert_float4_to_u32(imgui.ImVec4(H,S,V,1))
    # color[0],color[1],color[2]=imgui.color_convert_hsv_to_rgb(H, 1, 1,color[0],color[1],color[2])
    # print('backup_initial_col', color)
    # print('backup_initial_colabc', a,b,c)
    # abc=imgui.ImVec4(1,1,1,1)
    # abc=imgui.ImVec4(*(imgui.color_convert_hsv_to_rgb(H, 1, 1,abc.x,abc.y,abc.z)),1)
    # print('backup_initial_colabc convert', abc)
    # print('backup_initial_col', H, S, V)
    # print('backup_initial_col', color[0], color[1], color[2])
    # return value_changed,
def convert_color_float(h, s, v, alpha=1):
    """ Convert HSV to RGBA format and get ImU32 color value. """
    r, g, b = 0.0, .0, .0
    r, g, b = imgui.color_convert_hsv_to_rgb(h, s, v, r, g, b)  # Convert HSV to RGB
    return imgui.ImVec4(r, g, b , alpha)
def convert_color(h, s, v, alpha=255):
    """ Convert HSV to RGBA format and get ImU32 color value. """
    r, g, b = 0.0, .0, .0
    r, g, b = imgui.color_convert_hsv_to_rgb(h, s, v, r, g, b)  # Convert HSV to RGB
    return imgui.get_color_u32(imgui.ImVec4((r * 255), int(g * 255), int(b * 255), alpha))
