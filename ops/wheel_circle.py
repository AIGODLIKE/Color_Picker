def wheel_circle():
    import imgui

    width = imgui.calculate_item_width()
    style = imgui.get_style()
    square_sz = imgui.get_frame_height()  # float square_sz = GetFrameHeight()
    draw_list: "imgui.core._DrawList" = imgui.get_window_draw_list()
    picker_pos = imgui.get_cursor_pos()

    bars_width = square_sz
    sv_picker_size = max(bars_width * 1, width - 1 * (bars_width + style.item_inner_spacing.x))

    wheel_thickness = sv_picker_size * 0.08
    wheel_r_outer = sv_picker_size * 0.50
    wheel_r_inner = wheel_r_outer - wheel_thickness

    aeps = 0.5 / wheel_r_outer
    segment_per_arc = max(4, int(wheel_r_outer / 12))

    wheel_center = imgui.Vec2(picker_pos.x + (sv_picker_size + bars_width) * 0.5, picker_pos.y + sv_picker_size * 0.5)

    imgui.invisible_button('hsv',
                           sv_picker_size + style.item_inner_spacing.x + bars_width,
                           sv_picker_size
                           )

    for n in range(6):
        a0 = n / 6.0 * 2.0 * pi - aeps
        a1 = n + 1. / 6.0 * 2.0 * pi + aeps
        vert_start_idx = draw_list.vtx_buffer_size
        draw_list.path_arc_to(wheel_center, (wheel_r_inner + wheel_r_outer) * 0.5, a0, a1, segment_per_arc)
        draw_list.path_stroke(col_white, 0, wheel_thickness)
        vert_end_idx = draw_list.vtx_buffer_size

        gradient_p0 = imgui.Vec2(wheel_center.x + cos(a0) * wheel_r_inner, wheel_center.y + sin(a0) * wheel_r_inner)
        gradient_p1 = imgui.Vec2(wheel_center.x + cos(a1) * wheel_r_inner, wheel_center.y + sin(a1) * wheel_r_inner)
        imgui.internal.shade
    #
    # cos_hue_angle = cos(H * 2.0 * pi)
    # sin_hue_angle = sin(H * 2.0 * pi)
    # hue_cursor_pos = imgui.Vec2(wheel_center.x + cos_hue_angle * (wheel_r_inner + wheel_r_outer) * 0.5, wheel_center.y + sin_hue_angle * (wheel_r_inner + wheel_r_outer) * 0.5)
    # float hue_cursor_rad = value_changed_h ? wheel_thickness * 0.65f : wheel_thickness * 0.55f;
    # int hue_cursor_segments = draw_list->_CalcCircleAutoSegmentCount(hue_cursor_rad); // Lock segment count so the +1 one matches others.
    # draw_list->AddCircleFilled(hue_cursor_pos, hue_cursor_rad, hue_color32, hue_cursor_segments);
    # draw_list->AddCircle(hue_cursor_pos, hue_cursor_rad + 1, col_midgrey, hue_cursor_segments);
    # draw_list->AddCircle(hue_cursor_pos, hue_cursor_rad, col_white, hue_cursor_segments);
    #
    # // Render SV triangle (rotated according to hue)
    # ImVec2 tra = wheel_center + ImRotate(triangle_pa, cos_hue_angle, sin_hue_angle);
    # ImVec2 trb = wheel_center + ImRotate(triangle_pb, cos_hue_angle, sin_hue_angle);
    # ImVec2 trc = wheel_center + ImRotate(triangle_pc, cos_hue_angle, sin_hue_angle);
    # ImVec2 uv_white = GetFontTexUvWhitePixel();
    # draw_list->PrimReserve(3, 3);
    # draw_list->PrimVtx(tra, uv_white, hue_color32);
    # draw_list->PrimVtx(trb, uv_white, col_black);
    # draw_list->PrimVtx(trc, uv_white, col_white);
    # draw_list->AddTriangle(tra, trb, trc, col_midgrey, 1.5f);
    # sv_cursor_pos = ImLerp(ImLerp(trc, tra, ImSaturate(S)), trb, ImSaturate(1 - V));


def ShadeVertsLinearColorGradientKeepAlpha(draw_lise, vert_start_idx, vert_end_idx, gradient_p0, gradient_p1, col0,
                                           col1):
    gradient_extent = gradient_p1 - gradient_p0
    gradient_inv_length2 = 1.0 / ImLengthSqr(gradient_extent)
    vert_start = draw_list.vtx_buffer_data + vert_start_idx
    vert_end = draw_list.vtx_buffer_data + vert_end_idx
    col0_r = int(col0 >> IM_COL32_R_SHIFT) & 0xFF
    col0_g = int(col0 >> IM_COL32_G_SHIFT) & 0xFF
    col0_b = int(col0 >> IM_COL32_B_SHIFT) & 0xFF
    col_delta_r = (int(col1 >> IM_COL32_R_SHIFT) & 0xFF) - col0_r
    col_delta_g = (int(col1 >> IM_COL32_G_SHIFT) & 0xFF) - col0_g
    col_delta_b = (int(col1 >> IM_COL32_B_SHIFT) & 0xFF) - col0_b

    # vert = vert_start
    # while vert < vert_end:
    #     d = ImDot(vert->pos - gradient_p0, gradient_extent);
    #     t = ImClamp(d * gradient_inv_length2, 0.0
    #     f, 1.0
    #     f);
    #     r = int(col0_r + col_delta_r * t)
    #     g = int(col0_g + col_delta_g * t)
    #     b = int(col0_b + col_delta_b * t)
    #     vert->col = (r << IM_COL32_R_SHIFT) | (g << IM_COL32_G_SHIFT) | (b << IM_COL32_B_SHIFT) | (vert
    #                                                                                                ->col & IM_COL32_A_MASK);
    #     vert += 1


def ImLengthSqr(lhs):
    return (lhs.x * lhs.x) + (lhs.y * lhs.y)


def ImDot(a, b):
    return a.x * b.x + a.y * b.y
