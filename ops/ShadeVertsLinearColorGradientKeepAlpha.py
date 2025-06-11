# // Generic linear color gradient, write to RGB fields, leave A untouched.
# void ImGui::ShadeVertsLinearColorGradientKeepAlpha(ImDrawList* draw_list, int vert_start_idx, int vert_end_idx, ImVec2 gradient_p0, ImVec2 gradient_p1, ImU32 col0, ImU32 col1)
# {
#     ImVec2 gradient_extent = gradient_p1 - gradient_p0;
#     float gradient_inv_length2 = 1.0f / ImLengthSqr(gradient_extent);
#     ImDrawVert* vert_start = draw_list->VtxBuffer.Data + vert_start_idx;
#     ImDrawVert* vert_end = draw_list->VtxBuffer.Data + vert_end_idx;
#     const int col0_r = (int)(col0 >> IM_COL32_R_SHIFT) & 0xFF;
#     const int col0_g = (int)(col0 >> IM_COL32_G_SHIFT) & 0xFF;
#     const int col0_b = (int)(col0 >> IM_COL32_B_SHIFT) & 0xFF;
#     const int col_delta_r = ((int)(col1 >> IM_COL32_R_SHIFT) & 0xFF) - col0_r;
#     const int col_delta_g = ((int)(col1 >> IM_COL32_G_SHIFT) & 0xFF) - col0_g;
#     const int col_delta_b = ((int)(col1 >> IM_COL32_B_SHIFT) & 0xFF) - col0_b;
#     for (ImDrawVert* vert = vert_start; vert < vert_end; vert++)
#     {
#         float d = ImDot(vert->pos - gradient_p0, gradient_extent);
#         float t = ImClamp(d * gradient_inv_length2, 0.0f, 1.0f);
#         int r = (int)(col0_r + col_delta_r * t);
#         int g = (int)(col0_g + col_delta_g * t);
#         int b = (int)(col0_b + col_delta_b * t);
#         vert->col = (r << IM_COL32_R_SHIFT) | (g << IM_COL32_G_SHIFT) | (b << IM_COL32_B_SHIFT) | (vert->col & IM_COL32_A_MASK);
#     }
# }
from ..utils import im_length_sqr

def shade_verts_linear_color_gradient_keep_alpha(
        draw_list,
        vert_start_idx, vert_end_idx, gradient_p0, gradient_p1, col0, col1
):
    import imgui
    gradient_extent = gradient_p1 - gradient_p0
    gradient_inv_length2 = 1.0 / im_length_sqr(gradient_extent)
    # imgui.vertex_buffer_vertex_size()
    # imgui.get_window_draw_list().vert
    vert_start = vert_start_idx
    vert_end = vert_end_idx

    col0_r = col0 >> IM_COL32_R_SHIFT) & 0xFF
    col0_g = col0 >> IM_COL32_G_SHIFT) & 0xFF
    col0_b = col0 >> IM_COL32_B_SHIFT) & 0xFF
    #     const int col_delta_r = ((int)(col1 >> IM_COL32_R_SHIFT) & 0xFF) - col0_r;
    #     const int col_delta_g = ((int)(col1 >> IM_COL32_G_SHIFT) & 0xFF) - col0_g;
    #     const int col_delta_b = ((int)(col1 >> IM_COL32_B_SHIFT) & 0xFF) - col0_b;
    #     for (ImDrawVert* vert = vert_start; vert < vert_end; vert++)
    #     {
    #         float d = ImDot(vert->pos - gradient_p0, gradient_extent);
    #         float t = ImClamp(d * gradient_inv_length2, 0.0f, 1.0f);
    #         int r = (int)(col0_r + col_delta_r * t);
    #         int g = (int)(col0_g + col_delta_g * t);
    #         int b = (int)(col0_b + col_delta_b * t);
    #         vert->col = (r << IM_COL32_R_SHIFT) | (g << IM_COL32_G_SHIFT) | (b << IM_COL32_B_SHIFT) | (vert->col & IM_COL32_A_MASK);
    #     }