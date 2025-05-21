color_hsv = [0, 0, 0]
color_rgb = [0, 0, 0]
colors = []
color_palette_size = 40
color_palette_dict = {}
# colorbar 颜色拾取处理,拖动bar的最后一个色彩存入colors[0]
color_tmp = []

values = [0.0, 0.60, 0.35, 0.9, 0.70, 0.20, 0.0]
Color_Picker_Imgui_color = (114, 144, 154, 200)
Color_Picker_Imgui_alpha_preview = True
Color_Picker_Imgui_alpha_half_preview = False
Color_Picker_Imgui_drag_and_drop = True
Color_Picker_Imgui_options_menu = True
Color_Picker_Imgui_hdr = False
from ..utils import get_pref


class ImguiColorPicker:
    def draw_color_picker(self):
        import imgui
        start_pos = imgui.Vec2(imgui.get_cursor_pos().x, +imgui.get_cursor_pos().y + 10)
        imgui.set_cursor_pos(start_pos)

    def old(self):
        im_cf = imgui.ColorEditFlags_
        if get_pref().picker_switch:
            picker_type = im_cf.picker_hue_wheel

        else:
            picker_type = im_cf.picker_hue_bar
        misc_flags = picker_type | im_cf.no_options | im_cf.input_rgb | im_cf.no_alpha | im_cf.no_side_preview | im_cf.no_label

        color = get_brush_color_based_on_mode()
        if imgui.is_mouse_clicked(0):
            self.pre_color = copy.deepcopy(color)

        colorpicker_changed, picker_pos, picker_pos2, wheel_center = colorpicker('##aa', color, misc_flags, self)
        imgui.same_line()
        imgui.begin_group()
        global color_hsv, color_rgb, color_tmp, color_palette_dict
        color_bar_changed = color_bar(color, color_hsv, color_rgb, self)
        if imgui.is_mouse_down(0):
            if color_bar_changed:
                color_tmp = copy.deepcopy(color)
            id = imgui.get_current_context().hovered_id
            if hasattr(color_palette_dict, f'c{id}'):
                self.color_palette.insert(0, copy.deepcopy(color_palette_dict[id]))
        elif imgui.is_mouse_released(0):
            if colorpicker_changed:
                self.color_palette.insert(0, copy.deepcopy(color))

        if imgui.is_mouse_released(0):
            if color_tmp != [] and not colorpicker_changed:

                ids = [imgui.get_id(i) for i in ['H ', 'S ', 'V ', 'R ', 'G ', 'B ']]
                if imgui.get_current_context().hovered_id in ids:
                    self.color_palette.insert(0, copy.deepcopy(color_tmp))
        color_palette('##color_palette', color, self.backup_color, self.pre_color, self.color_palette)
        imgui.end_group()
        picker_switch_button(' ##1')
        start_pos = imgui.Vec2(imgui.get_cursor_pos().x, imgui.get_cursor_pos().y - 15)
        imgui.set_cursor_pos(start_pos)
        imgui.text('')
        # imgui.show_demo_window()
        self.track_any_cover()
        if imgui.is_item_hovered():
            imgui.set_keyboard_focus_here(-1)
