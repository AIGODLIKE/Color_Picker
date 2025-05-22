def color_picker4(label, color, flags, ref_col):
    import imgui
    g = imgui.get_current_context()

    # ImGuiWindow* window = GetCurrentWindow();
    # if (window->SkipItems)
    #     return false;
    draw_list = imgui.get_window_draw_list()
    style = imgui.get_style()
    io = imgui.get_io()
    width = imgui.calculate_item_width()

    # const bool is_readonly = ((g.NextItemData.ItemFlags | g.CurrentItemFlags) & ImGuiItemFlags_ReadOnly) != 0;
    # g.NextItemData.ClearFlags();
    imgui.push_id(label)
    # id = imgui.COLOR_EDIT_I
    imgui.begin_group()
