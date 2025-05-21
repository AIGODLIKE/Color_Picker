import copy
import math

import bpy

from .utils import set_brush_color_based_on_mode, brush_value_based_on_mode

color_edit_active_component = None
slider_width = 256


def im_clamp(v, mn, mx):
    return max(mn, min(mx, v))


def color_edit_restore_hs(color, H, S, V):
    import imgui
    g_Gimgui = imgui.get_current_context()
    assert g_Gimgui.color_edit_current_id != 0, 'ColorEditCurrentID should not be zero'
    if (
            g_Gimgui.color_edit_saved_id != g_Gimgui.color_edit_current_id or g_Gimgui.color_edit_saved_color != imgui.color_convert_float4_to_u32(
        imgui.Vec4(color[0], color[1], color[2], 0))):
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
    import imgui
    g_Gimgui = imgui.get_current_context()
    assert g_Gimgui.color_edit_current_id != 0
    if g_Gimgui.color_edit_saved_id!=g_Gimgui.color_edit_current_id or g_Gimgui.color_edit_saved_color != imgui.color_convert_float4_to_u32(imgui.Vec4(color[0], color[1], color[2], 0)):
        return H
    # print('g_Gimgui.color_edit_saved_hue',g_Gimgui.color_edit_saved_hue)
    return g_Gimgui.color_edit_saved_hue if g_Gimgui.color_edit_saved_hue is not None else H
def get_wheeL_tri(mouse_pos):
    import imgui

    sv_picker_size = 256
    # print('三角sv_picker_size',sv_picker_size)
    # square_sz = imgui.get_frame_height()
    square_sz = 19
    # print('三角square_sz',square_sz)
    bars_width = square_sz
    region=bpy.context.region
    # print('region',region.height)
    picker_pos=imgui.Vec2(mouse_pos[0]-127,mouse_pos[1]+110)
    # print('三角picker_pos', picker_pos)
    # picker_pos=imgui.get_mouse_pos()
    wheel_thickness = sv_picker_size * 0.08
    wheel_r_outer = sv_picker_size * 0.50
    wheel_r_inner = wheel_r_outer - wheel_thickness
    wheel_center = imgui.Vec2(picker_pos.x + (sv_picker_size + bars_width) * 0.5,
                                picker_pos.y - sv_picker_size * 0.5)
    # print('三角 sv_picker_size * 0.5', sv_picker_size * 0.5)
    # print('三角wheel_center', wheel_center)
    # print('三角bars_width', bars_width)
    # print('三角sv_picker_size', sv_picker_size)

    triangle_r = wheel_r_inner - int(sv_picker_size * 0.027)
    triangle_pa = imgui.Vec2(triangle_r, 0.0)  # Hue point.
    triangle_pc = imgui.Vec2(triangle_r * -0.5,
                               triangle_r * -0.866025)  # White point.-0.5 和 -0.866025 分别是 cos(120°) 和 sin(120°) 的值。
    triangle_pb = imgui.Vec2(triangle_r * -0.5, triangle_r * +0.866025)
    tra = (wheel_center[0] + triangle_pa.x, wheel_center[1] + triangle_pa.y)
    trb = (wheel_center[0]+ triangle_pb.x, wheel_center[1] + triangle_pb.y)
    trc = (wheel_center[0]+ triangle_pc.x, wheel_center[1] + triangle_pc.y)
    a0 = (wheel_center[0] + 0, wheel_center[1] + triangle_pa.y)
    b0 = (wheel_center[0] + triangle_pb.x, wheel_center[1] + triangle_pb.y )
    b2 = (wheel_center[0] + triangle_pa.x, wheel_center[1] + triangle_pa.y)
    b4 = (wheel_center[0]+ triangle_pb.x, wheel_center[1] + triangle_pc.y)
    c0 = (wheel_center[0] + triangle_pc.x, wheel_center[1] + triangle_pa.y )
    c1 = (wheel_center[0] + triangle_r*0.25, wheel_center[1] + triangle_pb.y/2)
    c3 = (wheel_center[0] + triangle_r*0.25, wheel_center[1] - triangle_pb.y/2)
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
is_triangle = False

def draw_shape(draw_list, position, size, is_triangle):
    import imgui

    if is_triangle:
        draw_list.add_triangle_filled(
            imgui.Vec2(position[0] + size, position[1]+size),
            imgui.Vec2(position[0]-size, position[1] + size),
            imgui.Vec2(position[0] , position[1] -size),
            imgui.color_convert_float4_to_u32(imgui.Vec4(0.6, .6, .6, 0.05))
        )
        # print(11111)
    else:
        draw_list.add_rect_filled(
            imgui.Vec2(position[0]-size, position[1]-size),
            imgui.Vec2(position[0] + size, position[1] + size),
            imgui.color_convert_float4_to_u32(imgui.Vec4(0.6, .6, .6, 0.05))
        )
        # print(2222)

def picker_switch_button(label):
    import imgui
    # global is_triangle
    g_Gimgui = imgui.get_current_context()
    window = imgui.internal.get_current_window()
    # print('窗口坐标',imgui.get_cursor_pos(),imgui.get_window_pos(),imgui.get_cursor_start_pos())
    # if window.skip_items:
    #     return False
    draw_list = window.draw_list
    # print(2222, imgui.get_cursor_pos())
    pos=imgui.Vec2(window.dc.cursor_pos.x+2, window.dc.cursor_pos.y-8)
    imgui.set_cursor_pos(imgui.Vec2(imgui.get_cursor_pos().x+2,imgui.get_cursor_pos().y-8))
    size = 20
    # print(1111,imgui.get_cursor_pos())
    center = imgui.Vec2(pos.x +size/2,pos.y +size/2)
    imgui.push_style_color(21, imgui.Vec4(0, 0, 0, 0.1))
    imgui.push_style_color(22, imgui.Vec4(0, 0, 0, 0.1))
    imgui.push_style_color(23, imgui.Vec4(0, 0, 0, 0.1))
    from .utils import get_prefs
    # print(hasattr(bpy.context.preferences, 'addons'))
    if hasattr(bpy.context.preferences, 'addons'):
        pref=get_prefs()
    # is_triangle=pref.picker_switch
    # 绘制按钮
    if imgui.button(label,imgui.Vec2(size,size)):
        pref.picker_switch=not pref.picker_switch
        # is_triangle = not is_triangle
    imgui.pop_style_color(3)
    # 绘制图形


    # print(pos)
    draw_shape(draw_list, center, size/2, pref.picker_switch)
def colorpicker(label, color, flags, ops):
    import imgui
    # 拾取器 上下文
    g_Gimgui = imgui.get_current_context()
    window = imgui.internal.get_current_window()
    # print('窗口坐标',imgui.get_cursor_pos(),imgui.get_window_pos(),imgui.get_cursor_start_pos())
    if window.skip_items:
        return False
    draw_list = window.draw_list
    style = g_Gimgui.style
    io = g_Gimgui.io
    # id=window.get_id(label)

    # 检查各种标志
    width = imgui.calc_item_width()

    is_readonly = ((g_Gimgui.next_item_data.item_flags | g_Gimgui.current_item_flags) & imgui.internal.ItemFlags_.read_only) != 0
    g_Gimgui.next_item_data.clear_flags()
    # 唯一标识符
    imgui.push_id(label)
    imgui.begin_group()


    set_current_color_edit_id = (g_Gimgui.color_edit_current_id == 0)
    # 当前窗口的顶部ID将作为当前颜色编辑器的ID
    if set_current_color_edit_id:
        g_Gimgui.color_edit_current_id = window.id_stack.__getitem__(window.id_stack.size() - 1)


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
    picker_pos = imgui.Vec2(window.dc.cursor_pos.x, window.dc.cursor_pos.y)
    picker_pos2=imgui.get_cursor_pos()
    # picker_pos = imgui.get_window_pos()


    square_sz = imgui.get_frame_height()

    bars_width = square_sz

    sv_picker_size = max(bars_width * 1, width - (bars_width + style.item_inner_spacing.x))  # Saturation / Value picking box
    sv_picker_size = max(bars_width * 1, 256)  # Saturation / Value picking box
    bar0_pos_x = picker_pos.x + sv_picker_size + style.item_inner_spacing.x
    # print('bar0_pos_x',bar0_pos_x)
    bar1_pos_x = bar0_pos_x + bars_width + style.item_inner_spacing.x
    bars_triangles_half_sz = imgui.internal.im_trunc(bars_width * 0.20)


    wheel_thickness = sv_picker_size * 0.08
    wheel_r_outer = sv_picker_size * 0.50
    wheel_r_inner = wheel_r_outer - wheel_thickness
    wheel_center = imgui.Vec2(picker_pos.x + (sv_picker_size + bars_width) * 0.5,
                                picker_pos.y + sv_picker_size * 0.5)
    # 该三角形被显示为旋转状态, 其中triangle_pa指向色调(Hue)
    # 方向, 但大部分坐标仍保持未旋转, 用于逻辑计算。
    triangle_r = wheel_r_inner - int(sv_picker_size * 0.027)
    triangle_pa = imgui.Vec2(triangle_r, 0.0)  # Hue point.
    triangle_pc = imgui.Vec2(triangle_r * -0.5, triangle_r * -0.866025)  # White point.-0.5 和 -0.866025 分别是 cos(120°) 和 sin(120°) 的值。
    triangle_pb = imgui.Vec2(triangle_r * -0.5, triangle_r * +0.866025)  # Black  point.-0.5 和 0.866025 分别是 cos(240°) 和 sin(240°) 的值
    sqrt2=1.4142135
    quad_size=2*triangle_r /  sqrt2
    offset_l_up = imgui.Vec2(triangle_r /-sqrt2, triangle_r / -sqrt2)
    offset_r_bot = imgui.Vec2(triangle_r/ sqrt2, triangle_r /  sqrt2)
    # print(triangle_pc.y,triangle_pb.y)
    # print(triangle_pc.y-triangle_pb.y)
    H = color.hsv[0]
    S = color.hsv[1]
    V = color.hsv[2]
    R = color[0]
    G = color[1]
    B = color[2]
    # print('imgui picker_pos3111222', picker_pos)
    if flags & imgui.ColorEditFlags_.input_rgb:

        H, S, V = imgui.color_convert_rgb_to_hsv(R, G, B, H, S, V)
        # print('11', H, S, V)
        H, S, V = color_edit_restore_hs(color.hsv, H, S, V)
        # print('22', H, S, V)
    elif flags & imgui.ColorEditFlags_.input_hsv:
        R, G, B = imgui.color_convert_hsv_to_rgb(H, S, V, R, G, B)
        # print('33', R, G, B)
    # 初始化变量，用于跟踪颜色值的变化
    value_changed = False
    value_changed_h = False
    value_changed_sv = False
    # 设置当前UI元素不响应键盘导航，以免影响色相选择
    imgui.internal.push_item_flag(imgui.internal.ItemFlags_.no_nav, True)
    global color_edit_active_component
    # 如果设置了色相环选择标志，则执行色相环和SV三角形的逻辑
    if flags & imgui.ColorEditFlags_.picker_hue_wheel:
        imgui.invisible_button('hsv', imgui.Vec2(sv_picker_size + style.item_inner_spacing.x + bars_width,
                                                   sv_picker_size))
        # print('activce', imgui.is_item_active(), 'read ', is_readonly)
        # 全局变量用于跟踪当前激活的控件


        # 检查是否需要更新当前激活的控件
        if imgui.is_item_active() and color_edit_active_component is None:
            initial_off = imgui.Vec2(g_Gimgui.io.mouse_pos_prev.x - wheel_center.x,g_Gimgui.io.mouse_pos_prev.y - wheel_center.y)
            initial_dist2 = imgui.internal.im_length_sqr(initial_off)
            if imgui.internal.im_triangle_contains_point(triangle_pa, triangle_pb, triangle_pc, initial_off):
                color_edit_active_component = 'triangle'
            elif initial_dist2 >= ((wheel_r_inner - 1) * (wheel_r_inner - 1)) and initial_dist2 <= (
                    (wheel_r_outer + 1) * (wheel_r_outer + 1)):
                color_edit_active_component = 'wheel'

        # 检查当前激活的控件并更新颜色值
        if color_edit_active_component == 'triangle':
            current_off_unrotated = imgui.Vec2(g_Gimgui.io.mouse_pos.x - wheel_center.x,g_Gimgui.io.mouse_pos.y - wheel_center.y)
            if not imgui.internal.im_triangle_contains_point(triangle_pa, triangle_pb, triangle_pc,
                                                             current_off_unrotated):
                current_off_unrotated = imgui.internal.im_triangle_closest_point(triangle_pa, triangle_pb, triangle_pc,
                                                                                 current_off_unrotated)

            uu, vv, ww = 0.0, 0.0, 0.0
            uu, vv, ww = imgui.internal.im_triangle_barycentric_coords(triangle_pa, triangle_pb, triangle_pc,
                                                                       current_off_unrotated, uu, vv, ww)
            V = im_clamp(1.0 - vv, 0.0001, 1.0)
            S = im_clamp(uu / V, 0.0001, 1.0)
            value_changed = value_changed_sv = True

        elif color_edit_active_component == 'wheel':
            current_off = imgui.Vec2(g_Gimgui.io.mouse_pos.x - wheel_center.x,g_Gimgui.io.mouse_pos.y - wheel_center.y)
            H = math.atan2(current_off.y, current_off.x) / math.pi * 0.5
            if H < .0:
                H += 1.0
            value_changed = value_changed_h = True

        # 重置激活的控件状态
        if not imgui.is_item_active():
            color_edit_active_component = None
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
    elif flags & imgui.ColorEditFlags_.picker_hue_bar:
        imgui.invisible_button('hsv', imgui.Vec2(sv_picker_size + style.item_inner_spacing.x + bars_width,
                                                   sv_picker_size))
        # 检查是否需要更新当前激活的控件
        if imgui.is_item_active() and color_edit_active_component is None:
            initial_off = imgui.Vec2(g_Gimgui.io.mouse_pos_prev.x - wheel_center.x,g_Gimgui.io.mouse_pos_prev.y - wheel_center.y)
            initial_dist2 = imgui.internal.im_length_sqr(initial_off)
            quad_l_up = imgui.Vec2(wheel_center.x + offset_l_up.x,wheel_center.y + offset_l_up.y)
            quad_r_bot =imgui.Vec2( wheel_center.x + offset_r_bot.x,wheel_center.y + offset_r_bot.y)

            if (quad_l_up.x <= io.mouse_pos.x <= quad_r_bot.x and
                    quad_l_up.y <= io.mouse_pos.y <= quad_r_bot.y):
                color_edit_active_component = 'square'
            if  initial_dist2 >= ((wheel_r_inner - 1) * (wheel_r_inner - 1)) and initial_dist2 <= (
                    (wheel_r_outer + 1) * (wheel_r_outer + 1)):
                color_edit_active_component = 'wheel'

        # 检查当前激活的控件并更新颜色值
        if color_edit_active_component == 'square':
            l_up=imgui.Vec2(wheel_center.x + offset_l_up.x,wheel_center.y + offset_l_up.y)
            S = imgui.internal.im_saturate((io.mouse_pos.x - l_up.x) / (quad_size - 1))
            V = 1.0 - imgui.internal.im_saturate((io.mouse_pos.y - l_up.y) / (quad_size - 1))
            # print(H)
            H=color_edit_restore_h(color,H)
            # print('H=color_edit_restore_h(color,H)',H)
            # H,S,V=color_edit_restore_hs(color,H,S,V)
            value_changed = value_changed_sv = True

        elif  color_edit_active_component == 'wheel':
            current_off = imgui.Vec2(g_Gimgui.io.mouse_pos.x - wheel_center.x,g_Gimgui.io.mouse_pos.y - wheel_center.y)
            H = math.atan2(current_off.y, current_off.x) / math.pi * 0.5
            if H < .0:
                H += 1.0
            # print('wheel',H)
            value_changed = value_changed_h = True
            # 重置激活的控件状态
        if not imgui.is_item_active():
            color_edit_active_component = None
        # print('imgui picker_p12322113', picker_pos)
        imgui.set_cursor_screen_pos(imgui.Vec2(bar0_pos_x, picker_pos.y))
        # print('imgui picker_pos231311113', picker_pos)
        # imgui.invisible_button("hue", imgui.Vec2(bars_width, sv_picker_size))

    if alpha_bar:
        pass
    imgui.internal.pop_item_flag()
    if value_changed_h or value_changed_sv:
        if flags & imgui.ColorEditFlags_.input_rgb:

            color[0],color[1],color[2]=imgui.color_convert_hsv_to_rgb(H, S, V, color[0],color[1],color[2])
            g_Gimgui.color_edit_saved_hue = H
            g_Gimgui.color_edit_saved_sat = S
            g_Gimgui.color_edit_saved_id = g_Gimgui.color_edit_current_id
            g_Gimgui.color_edit_saved_color = imgui.color_convert_float4_to_u32(
                imgui.Vec4(color[0], color[1], color[2], 0.0))
        elif flags & imgui.ColorEditFlags_.input_hsv:
            color.h = H
            color.s = S
            color.v = V
    value_changed_fix_hue_wrap = False
    if value_changed_fix_hue_wrap and (flags & imgui.ColorEditFlags_.input_rgb):
        new_H, new_S, new_V = .0, .0, .0
        new_H, new_S, new_V = imgui.color_convert_rgb_to_hsv(color.h, color.s, color.v, new_H, new_S, new_V)
        if new_H <= .0 and H > .0:
            pass
            if new_V <= 0 and V != new_V:
                color[0], color[1], color[2] = imgui.color_convert_hsv_to_rgb(H, S, V * 0.5 if new_V <= 0 else new_V,
                                                                              color[0], color[1], color[2])
                color.hsv = (H, S, V)
            elif new_S <= 0:
                color[0], color[1], color[2] = imgui.color_convert_hsv_to_rgb(H, S * 0.5 if new_S <= 0 else new_S,
                                                                              color[0], color[1], color[2])
                color.hsv=(H,S,V)
    if value_changed:
        if flags & imgui.ColorEditFlags_.input_rgb:
            R = color[0]
            G = color[1]
            B = color[2]
            H, S, V=imgui.color_convert_rgb_to_hsv(R, G, B, H, S, V)
            H, S, V = color_edit_restore_hs(color, H, S, V)
        elif flags & imgui.ColorEditFlags_.input_hsv:
            H = color.h
            S = color.s
            V = color.v
            R, G, B=imgui.color_convert_hsv_to_rgb(H, S, V, R, G, B)

    col_black = imgui.color_convert_float4_to_u32(imgui.Vec4(0.0,0.0,0.0, 1.0))
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
    # print('hue_color_f',hue_color_f)
    hue_color_f = imgui.Vec4(*(imgui.color_convert_hsv_to_rgb(H, 1, 1, hue_color_f.x, hue_color_f.y, hue_color_f.z)),
                               1)

    # print('hue_color_f2', hue_color_f)
    hue_color32 = imgui.color_convert_float4_to_u32(hue_color_f)
    user_col32_striped_of_alpha = imgui.color_convert_float4_to_u32(
        imgui.Vec4(R, G,B,1))  # Important: this is still including the main rendering / style alpha!!


    #圆环
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
    cos_hue_angle = math.cos(H * 2.0 * math.pi)
    sin_hue_angle = math.sin(H * 2.0 * math.pi)
    hue_cursor_pos = imgui.Vec2(wheel_center.x + cos_hue_angle * (wheel_r_inner + wheel_r_outer) * 0.5,
                                  wheel_center.y + sin_hue_angle * (wheel_r_inner + wheel_r_outer) * 0.5)

    hue_cursor_rad = wheel_thickness * 0.65 if value_changed_h else wheel_thickness * 0.55
    # print('hue_cursor_rad', hue_cursor_rad)
    # hue_cursor_rad = 5.0
    hue_cursor_segments = imgui.get_window_draw_list()._calc_circle_auto_segment_count(hue_cursor_rad)
    imgui.get_window_draw_list().add_circle_filled(hue_cursor_pos, hue_cursor_rad, hue_color32, hue_cursor_segments)
    imgui.get_window_draw_list().add_circle(hue_cursor_pos, hue_cursor_rad + 1, col_midgrey, hue_cursor_segments)
    imgui.get_window_draw_list().add_circle(hue_cursor_pos, hue_cursor_rad, col_white, hue_cursor_segments)

    # 圆环上的 按钮
    if flags & imgui.ColorEditFlags_.picker_hue_wheel:


        tra = imgui.Vec2((wheel_center.x + triangle_pa.x),(wheel_center.y + triangle_pa.y))
        trb = imgui.Vec2((wheel_center.x + triangle_pb.x),(wheel_center.y + triangle_pb.y))
        trc = imgui.Vec2((wheel_center.x + triangle_pc.x),(wheel_center.y + triangle_pc.y))
        uv_white = imgui.get_font_tex_uv_white_pixel()

        imgui.get_window_draw_list().prim_reserve(3, 3)
        imgui.get_window_draw_list().prim_vtx(tra, uv_white, hue_color32)
        imgui.get_window_draw_list().prim_vtx(trb, uv_white, col_black)
        imgui.get_window_draw_list().prim_vtx(trc, uv_white, col_white)
        imgui.get_window_draw_list().add_triangle(tra, trb, trc, col_midgrey, 0)
        sv_cursor_pos = imgui.internal.im_lerp(imgui.internal.im_lerp(trc, tra, imgui.internal.im_saturate(S)), trb,
                                               imgui.internal.im_saturate(1 - V))
    #绘制正方形
    elif flags & imgui.ColorEditFlags_.picker_hue_bar:
        # print('imgui picker_pos2', picker_pos)
        l_up=imgui.Vec2(wheel_center.x+offset_l_up.x,wheel_center.y+offset_l_up.y)
        r_bot=imgui.Vec2(wheel_center.x+offset_r_bot.x,wheel_center.y+offset_r_bot.y)

        draw_list.add_rect_filled_multi_color(l_up, r_bot, col_white, hue_color32, hue_color32, col_white)
        draw_list.add_rect_filled_multi_color(l_up, r_bot, 0, 0, col_black, col_black)
        imgui.internal.render_frame_border(l_up, r_bot, 0.0)
        # 彩色bar
        sv_cursor_pos=imgui.Vec2(0, 0)
        sv_cursor_pos.x = im_clamp(round((l_up).x + imgui.internal.im_saturate(S) * quad_size), (l_up).x + 2,
                                  picker_pos.x + sv_picker_size - 2)
        sv_cursor_pos.y=im_clamp(round((l_up).y + imgui.internal.im_saturate(1 - V) * quad_size), (l_up).y + 2, (l_up).y + quad_size - 2)
    sv_cursor_rad = wheel_thickness * 0.55 if value_changed_sv else wheel_thickness * 0.4
    sv_cursor_segments = imgui.get_window_draw_list()._calc_circle_auto_segment_count(sv_cursor_rad)
    # 游标颜色
    imgui.get_window_draw_list().add_circle_filled(sv_cursor_pos, sv_cursor_rad, user_col32_striped_of_alpha,
                                                   sv_cursor_segments)
    imgui.get_window_draw_list().add_circle(sv_cursor_pos, sv_cursor_rad + 1, col_midgrey, sv_cursor_segments)
    imgui.get_window_draw_list().add_circle(sv_cursor_pos, sv_cursor_rad, col_white, sv_cursor_segments)
    ops.sv_cursor_pos=sv_cursor_pos
    ops.sv_cursor_rad=sv_cursor_rad
    imgui.end_group()
    if value_changed and g_Gimgui.last_item_data.id_!=0:
        imgui.internal.mark_item_edited(g_Gimgui.last_item_data.id_)
    if set_current_color_edit_id:
        g_Gimgui.color_edit_current_id = 0
    imgui.pop_id()
    ops.h=H
    ops.s=S
    ops.v=V
    return value_changed,picker_pos,picker_pos2,wheel_center

def color_bar(color,color_hsv,color_rgb,ops):
    import imgui
    changed=False
    lines = ['H ', 'S ', 'V ', 'R ', 'G ', 'B ']
    imgui.begin_group()
    global color_bar, values
    hsv_or_rgb = {'hsv': False, 'rgb': False}
    slider_flag = imgui.SliderFlags_.no_input
    for i in range(6):
        # print('bar',color.h)
        # imgui.push_id(f'color_bar{lines[i]}')
        global slider_width
        imgui.set_next_item_width(slider_width)
        imgui.push_style_color(imgui.Col_.frame_bg, imgui.Vec4(1 / 7.0, 0.6, 1, 0))
        imgui.push_style_color(imgui.Col_.frame_bg_hovered, imgui.Vec4(1 / 7.0, .7, 1, 0))
        imgui.push_style_color(imgui.Col_.frame_bg_active, imgui.Vec4(1.0, 1.0, 1.0, 0))
        imgui.push_style_color(imgui.Col_.slider_grab, imgui.Vec4(0.9, 0.9, 0.9, 0.0))
        imgui.push_style_color(imgui.Col_.slider_grab_active, imgui.Vec4(0.9, 0.9, 0.9, 0.0))
        # imgui.push_style_color(imgui.Col_.border,imgui.Vec4(1/7.0, 1, 1,0))
        gradient_size = [imgui.calc_item_width(), 19]

        p0 = imgui.get_cursor_screen_pos()

        p1 = (p0.x + gradient_size[0], p0.y + gradient_size[1])
        if i == 0:
            col_hues = [
                imgui.get_color_u32(imgui.Vec4(1, 0, 0, 1)),  # 红色
                imgui.get_color_u32(imgui.Vec4(1, 1, 0, 1)),  # 黄色
                imgui.get_color_u32(imgui.Vec4(0, 1, 0, 1)),  # 绿色
                imgui.get_color_u32(imgui.Vec4(0, 1, 1, 1)),  # 青色
                imgui.get_color_u32(imgui.Vec4(0, 0, 1, 1)),  # 蓝色
                imgui.get_color_u32(imgui.Vec4(1, 0, 1, 1)),  # 品红
                imgui.get_color_u32(imgui.Vec4(1, 0, 0, 1))  # 红色(再次出现以闭合色环)
            ]
            for c in range(6):
                segment = gradient_size[0] / 6
                # 偏移两端
                if c == 0:
                    start = p0[0] + 2
                elif c == 5:
                    start = p0[0] - 2
                else:
                    start = p0[0]
                imgui.get_window_draw_list().add_rect_filled_multi_color(imgui.Vec2(start + c * segment, p0[1]),
                                                                         imgui.Vec2(start + (c + 1) * segment, p1[1]),
                                                                         col_hues[c], col_hues[c + 1], col_hues[c + 1],
                                                                         col_hues[c])
            imgui.get_window_draw_list().add_line(
                imgui.Vec2(p0[0] + 2 + (gradient_size[0] - 5) * ops.h, p0[1] - 3),
                imgui.Vec2(p0[0] + 2 + (gradient_size[0] - 5) * ops.h, p1[1] + 1),
                imgui.color_convert_float4_to_u32(imgui.Vec4(0.2, 0.2, 0.2, 1.0)),
                4
            )
            imgui.get_window_draw_list().add_line(
                imgui.Vec2(p0[0] + 2 + (gradient_size[0] - 5) * ops.h, p0[1] - 2),
                imgui.Vec2(p0[0] + 2 + (gradient_size[0] - 5) * ops.h, p1[1]),
                imgui.color_convert_float4_to_u32(imgui.Vec4(0.9, 0.9, 0.9, 1.0)),
                2
            )
            changed, ops.h = imgui.slider_float(lines[i], ops.h, 0.0, 1.0, "", slider_flag)
            hsv_or_rgb['hsv'] |= changed
        elif i == 1:
            imgui.get_window_draw_list().add_rect_filled_multi_color(imgui.Vec2(p0[0] + 2, p0[1]),
                                                                     imgui.Vec2(p1[0] - 2, p1[1]),
                                                                     convert_hsv2rgb32_color3(0, 0, ops.v),
                                                                     convert_hsv2rgb32_color3(ops.h, 1.0, ops.v),
                                                                     convert_hsv2rgb32_color3(ops.h, 1.0, ops.v),
                                                                     convert_hsv2rgb32_color3(0, 0, ops.v)
                                                                     )
            imgui.get_window_draw_list().add_line(
                imgui.Vec2(p0[0] + 2 + (gradient_size[0] - 5) * ops.s, p0[1] - 3),
                imgui.Vec2(p0[0] + 2 + (gradient_size[0] - 5) * ops.s, p1[1] + 1),
                imgui.color_convert_float4_to_u32(imgui.Vec4(0.2, 0.2, 0.2, 1.0)),
                4
            )
            imgui.get_window_draw_list().add_line(
                imgui.Vec2(p0[0] + 2 + (gradient_size[0] - 5) * ops.s, p0[1] - 2),
                imgui.Vec2(p0[0] + 2 + (gradient_size[0] - 5) * ops.s, p1[1]),
                imgui.color_convert_float4_to_u32(imgui.Vec4(0.9, 0.9, 0.9, 1.0)),
                2
            )
            changed, ops.s = imgui.slider_float(lines[i], ops.s, 0.0, 1.0, "", slider_flag)
            hsv_or_rgb['hsv'] |= changed
        elif i == 2:  # v
            imgui.get_window_draw_list().add_rect_filled_multi_color(imgui.Vec2(p0[0] + 2, p0[1]),
                                                                     imgui.Vec2(p1[0] - 2, p1[1]),
                                                                     convert_hsv2rgb32_color3(0, 0, 0),
                                                                     convert_hsv2rgb32_color3(color.h, color.s, 1),
                                                                     convert_hsv2rgb32_color3(color.h, color.s, 1),
                                                                     convert_hsv2rgb32_color3(0, 0, 0)
                                                                     )
            imgui.get_window_draw_list().add_line(
                imgui.Vec2(p0[0] + 2 + (gradient_size[0] - 5) * color.v, p0[1] - 3),
                imgui.Vec2(p0[0] + 2 + (gradient_size[0] - 5) * color.v, p1[1] + 1),
                imgui.color_convert_float4_to_u32(imgui.Vec4(0.2, 0.2, 0.2, 1.0)),
                4
            )
            imgui.get_window_draw_list().add_line(
                imgui.Vec2(p0[0] + 2 + (gradient_size[0] - 5) * color.v, p0[1] - 2),
                imgui.Vec2(p0[0] + 2 + (gradient_size[0] - 5) * color.v, p1[1]),
                imgui.color_convert_float4_to_u32(imgui.Vec4(0.9, 0.9, 0.9, 1.0)),
                2
            )
            changed, color_hsv[2] = imgui.slider_float(lines[i], color.v, 0.0, 1.0, "", slider_flag)
            hsv_or_rgb['hsv'] |= changed
        elif i == 3:  # r
            imgui.get_window_draw_list().add_rect_filled_multi_color(imgui.Vec2(p0[0] + 2, p0[1]),
                                                                     imgui.Vec2(p1[0] - 2, p1[1]),
                                                                     imgui.color_convert_float4_to_u32(
                                                                         imgui.Vec4(0, color.g, color.b, 1.0)),
                                                                     imgui.color_convert_float4_to_u32(
                                                                         imgui.Vec4(1, color.g, color.b, 1.0)),
                                                                     imgui.color_convert_float4_to_u32(
                                                                         imgui.Vec4(1, color.g, color.b, 1.0)),
                                                                     imgui.color_convert_float4_to_u32(
                                                                         imgui.Vec4(0, color.g, color.b, 1.0)),
                                                                     )
            imgui.get_window_draw_list().add_line(
                imgui.Vec2(p0[0] + 2 + (gradient_size[0] - 5) * color.r, p0[1] - 3),
                imgui.Vec2(p0[0] + 2 + (gradient_size[0] - 5) * color.r, p1[1] + 1),
                imgui.color_convert_float4_to_u32(imgui.Vec4(0.2, 0.2, 0.2, 1.0)),
                4
            )
            imgui.get_window_draw_list().add_line(
                imgui.Vec2(p0[0] + 2 + (gradient_size[0] - 5) * color.r, p0[1] - 2),
                imgui.Vec2(p0[0] + 2 + (gradient_size[0] - 5) * color.r, p1[1]),
                imgui.color_convert_float4_to_u32(imgui.Vec4(0.9, 0.9, 0.9, 1.0)),
                2
            )
            changed, color_rgb[0] = imgui.slider_float(lines[i], color.r, 0.0, 1.0, "", slider_flag)
            hsv_or_rgb['rgb'] |= changed
        elif i == 4:  # g
            imgui.get_window_draw_list().add_rect_filled_multi_color(imgui.Vec2(p0[0] + 2, p0[1]),
                                                                     imgui.Vec2(p1[0] - 2, p1[1]),
                                                                     imgui.color_convert_float4_to_u32(
                                                                         imgui.Vec4(color.r, 0, color.b, 1.0)),
                                                                     imgui.color_convert_float4_to_u32(
                                                                         imgui.Vec4(color.r, 1, color.b, 1.0)),
                                                                     imgui.color_convert_float4_to_u32(
                                                                         imgui.Vec4(color.r, 1, color.b, 1.0)),
                                                                     imgui.color_convert_float4_to_u32(
                                                                         imgui.Vec4(color.r, 0, color.b, 1.0)),
                                                                     )
            imgui.get_window_draw_list().add_line(
                imgui.Vec2(p0[0] + 2 + (gradient_size[0] - 5) * color.g, p0[1] - 3),
                imgui.Vec2(p0[0] + 2 + (gradient_size[0] - 5) * color.g, p1[1] + 1),
                imgui.color_convert_float4_to_u32(imgui.Vec4(0.2, 0.2, 0.2, 1.0)),
                4
            )
            imgui.get_window_draw_list().add_line(
                imgui.Vec2(p0[0] + 2 + (gradient_size[0] - 5) * color.g, p0[1] - 2),
                imgui.Vec2(p0[0] + 2 + (gradient_size[0] - 5) * color.g, p1[1]),
                imgui.color_convert_float4_to_u32(imgui.Vec4(0.9, 0.9, 0.9, 1.0)),
                2
            )
            changed, color_rgb[1] = imgui.slider_float(lines[i], color.g, 0.0, 1.0, "", slider_flag)
            hsv_or_rgb['rgb'] |= changed
        else:
            imgui.get_window_draw_list().add_rect_filled_multi_color(imgui.Vec2(p0[0] + 2, p0[1]),
                                                                     imgui.Vec2(p1[0] - 2, p1[1]),
                                                                     imgui.color_convert_float4_to_u32(
                                                                         imgui.Vec4(color.r, color.g, 0, 1.0)),
                                                                     imgui.color_convert_float4_to_u32(
                                                                         imgui.Vec4(color.r, color.g, 1, 1.0)),
                                                                     imgui.color_convert_float4_to_u32(
                                                                         imgui.Vec4(color.r, color.g, 1, 1.0)),
                                                                     imgui.color_convert_float4_to_u32(
                                                                         imgui.Vec4(color.r, color.g, 0, 1.0)),
                                                                     )
            imgui.get_window_draw_list().add_line(imgui.Vec2(p0[0] + 2 + (gradient_size[0] - 5) * color.b, p0[1] - 3),
                                                  imgui.Vec2(p0[0] + 2 + (gradient_size[0] - 5) * color.b, p1[1] + 1),
                                                  imgui.color_convert_float4_to_u32(imgui.Vec4(0.2, 0.2, 0.2, 1.0)),
                                                  4
                                                  )
            imgui.get_window_draw_list().add_line(
                imgui.Vec2(p0[0] + 2 + (gradient_size[0] - 5) * color.b, p0[1] - 2),
                imgui.Vec2(p0[0] + 2 + (gradient_size[0] - 5) * color.b, p1[1]),
                imgui.color_convert_float4_to_u32(imgui.Vec4(0.9, 0.9, 0.9, 1.0)),
                2
            )
            changed, color_rgb[2] = imgui.slider_float(lines[i], color.b, 0.0, 1.0, "", slider_flag, )
            hsv_or_rgb['rgb'] |= changed

        imgui.pop_style_color(5)
        # imgui.pop_id()
    imgui.end_group()

    # imgui.pop_id()
    if hsv_or_rgb['rgb']:
        set_brush_color_based_on_mode (color_rgb)
    elif hsv_or_rgb['hsv']:
        set_brush_color_based_on_mode([ops.h,ops.s,color_hsv[2]],'hsv')
    if hsv_or_rgb['rgb'] or hsv_or_rgb['hsv']:
        changed = True
    # print('bar',hsv_or_rgb['rgb'], hsv_or_rgb['hsv'],changed)
    return changed
def color_palette(label,color,backup_color,pre_color,colors):
    import imgui
    g_Gimgui = imgui.get_current_context()
    window = imgui.internal.get_current_window()
    # print('窗口坐标', imgui.get_cursor_pos(), imgui.get_window_pos(), imgui.get_cursor_start_pos())
    if window.skip_items:
        return False

    draw_list = window.draw_list
    style = g_Gimgui.style

    start_pos=imgui.Vec2(imgui.get_cursor_pos().x+1,imgui.get_cursor_pos().y)
    imgui.set_cursor_pos(start_pos)
    imgui.push_style_var(12, 0)
    imgui.push_style_var(14, imgui.Vec2(-2, -2))
    imgui.push_style_var(15, imgui.Vec2(-2, -2))
    imgui.begin_group()
    s_size=20
    flag=imgui.ColorEditFlags_.no_drag_drop
    changed=imgui.color_button('##current',imgui.Vec4(*color, 1.0),flag,imgui.Vec2(s_size*2.5-2,s_size*1.25))
    if imgui.color_button('##origin', imgui.Vec4(*backup_color, 1.0), flag, imgui.Vec2(s_size*1.25, 1.25*s_size)):
        tmp_c = []
        set_brush_color_based_on_mode(backup_color)
        colors.insert(0,backup_color)
    imgui.same_line()
    if imgui.color_button('##previous',imgui.Vec4(*(colors[1] if len(colors)>1 else pre_color), 1.0),flag,imgui.Vec2(s_size*1.25, 1.25*s_size)):
        set_brush_color_based_on_mode(colors[1] if len(colors)>1 else pre_color)
        colors.insert(0, colors[1] if len(colors)>1 else pre_color)
    imgui.end_group()
    imgui.pop_style_var(3)

    # try:


    imgui.same_line()
    imgui.begin_group()
    slider_start_pos = imgui.Vec2(imgui.get_cursor_pos().x - 4, imgui.get_cursor_pos().y + 1)
    slider_start_pos2 = imgui.Vec2(slider_start_pos.x, slider_start_pos.y + 27)  # strength
    imgui.set_cursor_pos(slider_start_pos)
    progress = 0.0
    progress_dir = 1.0
    progress += progress_dir * 0.4 * imgui.get_io().delta_time
    progress_saturated = im_clamp(progress, 0.0, 1.0)
    # size=bpy.context.scene.tool_settings.unified_paint_settings.size
    size=brush_value_based_on_mode(get=True,size=True)
    # strength=bpy.context.scene.tool_settings.unified_paint_settings.strength
    # strength = get_brush_strength_based_on_mode() brush_value_based_on_mode(get=True,strength=True)
    strength =brush_value_based_on_mode(get=True,strength=True)
    global slider_width
    slider_width_brush=slider_width-55
    # changed,size_f=imgui.slider_float('brush_size',size/500,.0,1,'',0)
    # bpy.context.scene.tool_settings.unified_paint_settings.size=max(1,int(size_f*500))
    imgui.push_style_color(imgui.Col_.frame_bg, imgui.Vec4(0.33, 0.33, 0.33, 1))
    imgui.push_style_color(imgui.Col_.plot_histogram, imgui.Vec4(0.3, 0.44, 0.7, 1))
    # imgui.push_style_color(imgui.Col_.frame_bg_active, imgui.Vec4(1.0, 1.0, 1.0, 0))

    imgui.progress_bar(size/200, imgui.Vec2(slider_width_brush, 20.0), 'R:{}'.format(size))
    imgui.set_cursor_pos(slider_start_pos2)
    imgui.progress_bar(strength, imgui.Vec2(slider_width_brush, 20.0), f'S:{strength:.3f}')
    imgui.pop_style_color(2)
    # sizef=bpy.context.scene.tool_settings.unified_paint_settings.size
    # for f in imgui.get_io().fonts.fonts:
    # print(len(imgui.get_io().fonts.fonts))

    if 480>=size>=190:
        v_max_r=500
        v_min_r=1
    elif size>480:
        v_max_r=1000
        v_min_r=480
    else:
        v_max_r=200
        v_min_r=1

    imgui.set_cursor_pos(slider_start_pos)

    flag=imgui.DragDropFlags_.source_no_preview_tooltip.value|imgui.SliderFlags_.no_input.value
    flag=imgui.SliderFlags_.no_input.value
    imgui.push_style_color(imgui.Col_.frame_bg, imgui.Vec4(1 / 7.0, 0.6, 1, 0))
    imgui.push_style_color(imgui.Col_.frame_bg_hovered, imgui.Vec4(1 / 7.0, .7, 1, 0))
    imgui.push_style_color(imgui.Col_.frame_bg_active, imgui.Vec4(1.0, 1.0, 1.0, 0))
    imgui.set_next_item_width(slider_width_brush)
    chan,size=imgui.drag_float('##Radius',size,1,v_min_r,v_max_r,'',flags=flag)
    imgui.set_cursor_pos(slider_start_pos2)
    imgui.set_next_item_width(slider_width_brush)
    chan,strength=imgui.drag_float('##Strength',strength,0.005,0.0,1.0,'',flags=flag)
    imgui.pop_style_color(3)
    brush_value_based_on_mode(set=True,size=int(size))
    # bpy.context.scene.tool_settings.unified_paint_settings.size = int(size)
    # set_brush_strength_based_on_mode(strength)
    brush_value_based_on_mode(set=True,strength=strength)
    imgui.end_group()
    # except:pass


    #color palette

    num=min(len(colors),36)
    imgui.push_style_var(12, 0)
    imgui.push_style_var(14, imgui.Vec2(1, 1))
    imgui.push_style_var(15, imgui.Vec2(1, 1))

    imgui.begin_group()
    start_pos = imgui.Vec2(imgui.get_cursor_pos().x+1 ,imgui.get_cursor_pos().y)
    imgui.set_cursor_pos(start_pos)
    if num:
        tmp_c=[]
        for i in range(num):
            if i%12==0:#0 12 24
                if i!=0:
                    start_pos = imgui.Vec2(imgui.get_cursor_pos().x+1 , imgui.get_cursor_pos().y+1)
                    imgui.set_cursor_pos(start_pos)
            else:

                imgui.same_line()
            if imgui.color_button(f'palette##{i}', imgui.Vec4(*colors[i], 1.0), flag, imgui.Vec2(s_size, s_size)):
                set_brush_color_based_on_mode(copy.deepcopy(colors[i]))
                tmp_c = copy.deepcopy(colors[i])

        if len(tmp_c):
            colors.insert(0, copy.deepcopy(tmp_c))
    imgui.end_group()
    imgui.pop_style_var(3)


def convert_hsv2rgb32_color3(h, s, v, alpha=255):
    import colorsys
    import imgui
    """ Convert HSV to RGB format and get ImU32 color value. """
    r, g, b = colorsys.hsv_to_rgb(h, s, v)  # Convert HSV to RGB

    return imgui.color_convert_float4_to_u32(imgui.Vec4(r, g, b, 1.0))
