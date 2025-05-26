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
import copy

from ..imgui_bundle.widget import colorpicker, picker_switch_button, color_palette
from ..utils import get_context_brush_color


class ImguiColorPicker:
    def draw_color_picker(self, context):
        from imgui_bundle import imgui
        # start_pos = imgui.ImVec2(imgui.get_cursor_pos().x, +imgui.get_cursor_pos().y + 10)
        # imgui.set_cursor_pos(start_pos)
        color = get_context_brush_color(context)

        imgui.begin_horizontal("Color")
        self.draw_left(context)
        self.draw_right(context)
        imgui.end_horizontal()

    def draw_left(self, context):
        from imgui_bundle import imgui
        imgui.begin_vertical("Left")

        self.draw_color_picker_wheel()
        picker_switch_button("a")

        imgui.end_vertical()

    def draw_right(self, context):
        from imgui_bundle import imgui
        imgui.begin_vertical("Right")

        color = get_context_brush_color(context)

        # color_bar(color, color, color, self)
        # color_palette("aaa", color, color, color, color)
        self.draw_h_bar()
        self.draw_s_bar()
        self.draw_v_bar()
        self.draw_r_bar()
        self.draw_g_bar()
        self.draw_b_bar()

        imgui.end_vertical()

    def old(self, context):

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
        start_pos = imgui.ImVec2(imgui.get_cursor_pos().x, imgui.get_cursor_pos().y - 15)
        imgui.set_cursor_pos(start_pos)
        imgui.text('')
        # imgui.show_demo_window()
        self.track_any_cover()
        if imgui.is_item_hovered():
            imgui.set_keyboard_focus_here(-1)