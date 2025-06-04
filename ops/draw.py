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

from ..utils import get_pref


class Draw:

    def draw_imgui(self, context):
        import imgui
        if self.draw_error:
            return
        self.create_context(context)
        # with imgui.push_style_color()
        # from ..imgui__aa.testwindow import show_test_window
        # show_test_window()
        # return


        imgui.push_style_var(imgui.STYLE_WINDOW_ROUNDING, 10)
        imgui.push_style_var(imgui.STYLE_WINDOW_BORDERSIZE, 0)

        imgui.get_io().display_size = (context.region.width, context.region.height)
        imgui.new_frame()
        self.start_window_pos(context)
        self.start_window(context)

        try:
            if self.show_test:
                imgui.show_demo_window()

            self.draw_color_picker(context)
            self.window_position = imgui.get_window_position()
            imgui.text("AAA")

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.draw_error = True
            self.report({'ERROR'}, str(e.args))

        # imgui.pop_style_var(2)
        imgui.end()
        imgui.end_frame()
        imgui.render()

        self.imgui_backend.render(imgui.get_draw_data())

    def start_window(self, context):
        import imgui

        window_flags = (
                # imgui.WINDOW_NO_TITLE_BAR |
                # imgui.WINDOW_NO_RESIZE |
                # imgui.WINDOW_ALWAYS_AUTO_RESIZE |
                imgui.WINDOW_NO_SCROLLBAR
            # imgui.WINDOW_NO_SCROLL_WITH_MOUSE
        )
        window_name = "Main Window"

        imgui.begin(window_name)
        # imgui.set_window_focus(window_name)

        start_pos = imgui.Vec2(imgui.get_cursor_pos().x, +imgui.get_cursor_pos().y)
        imgui.set_cursor_pos(start_pos)

    def start_window_pos(self, context):
        import imgui
        if self.window_position is None:
            x, y = self.mouse
            x, y = x - 50 - imgui.get_style().indent_spacing * 0.5, context.region.height - y - 129 - 10
            imgui.set_next_window_position(x, y)

    def draw_color_picker(self, context):
        import imgui
        imgui.same_line()

        self.draw_left(context)
        self.draw_right(context)

    def draw_left(self, context):
        import imgui
        with imgui.begin_group():
            start_pos = imgui.get_cursor_pos()
            # self.draw_switch_button()
            # imgui.set_cursor_pos(start_pos)
            # self.draw_color_picker_wheel(get_pref().picker_switch)
            # self.draw_demo_vertial_scrolling()

    def draw_right(self, context):
        import imgui

        with imgui.begin_group():
            self.draw_hsv_rgb()
            self.draw_brush_size()
            self.draw_brush_strength()
            self.draw_palettes()


    def draw_hsv_rgb(self):
        import imgui
        with imgui.begin_group():
            self.draw_h_bar()
            self.draw_s_bar()
            self.draw_v_bar()
            self.draw_r_bar()
            self.draw_g_bar()
            self.draw_b_bar()

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
        start_pos = imgui.Vec2(imgui.get_cursor_pos().x, imgui.get_cursor_pos().y - 15)
        imgui.set_cursor_pos(start_pos)
        imgui.text('')
        # imgui.show_demo_window()
        self.track_any_cover()
        if imgui.is_item_hovered():
            imgui.set_keyboard_focus_here(-1)