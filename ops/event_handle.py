import bpy


class ImguiEvent:
    handler = None

    # imgui
    io = None  # imgui.core._IO
    imgui_context = None  # imgui.core._ImGuiContext
    imgui_backend = None
    draw_error = None
    window_position = None

    show_test = False

    def register_imgui(self, context):
        from imgui_bundle import imgui

        self.create_context(context)

        self.handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_imgui, (context,), 'WINDOW', 'POST_PIXEL')
        self.draw_error = False
        self.window_position = None

    def unregister_imgui(self):
        bpy.types.SpaceView3D.draw_handler_remove(self.handler, 'WINDOW')

    def create_context(self, context):
        from .render import Renderer
        from imgui_bundle import imgui
        if self.imgui_context is None:
            self.imgui_context = imgui.create_context()
            self.imgui_backend = Renderer()
            self.imgui_backend.refresh_font_texture_ex()

    def draw_imgui(self, context):
        from imgui_bundle import imgui
        try:
            if self.draw_error:
                return
            self.create_context(context)
            imgui.get_io().display_size = (context.region.width, context.region.height)

            imgui.new_frame()
            self.start_window_pos(context)
            self.start_window(context)

            imgui.text("Hello world!")

            self.draw_color_picker(context)
            self.window_position = imgui.get_window_pos()
            if imgui.button("Show Test"):
                print("aaa", self.show_test)
                self.show_test = not self.show_test
            if self.show_test:
                imgui.show_demo_window()

            imgui.end()
            imgui.end_frame()
            imgui.render()
            self.imgui_backend.render(imgui.get_draw_data())
        except Exception:
            import traceback
            traceback.print_exc()
            self.draw_error = True

    def start_window(self, context):
        from imgui_bundle import imgui

        flags = imgui.WindowFlags_
        window_flags = (
                flags.no_title_bar |
                # flags.no_resize |
                flags.no_scrollbar |
                flags.always_auto_resize
            # flags.no_scroll_with_mouse
        )
        window_name = "Main Window"
        imgui.begin(window_name, False, window_flags)
        # imgui.set_window_focus(window_name)

        start_pos = imgui.ImVec2(imgui.get_cursor_pos().x, +imgui.get_cursor_pos().y + 10)
        imgui.set_cursor_pos(start_pos)

    def start_window_pos(self, context):
        from imgui_bundle import imgui
        if self.window_position is None:
            x, y = self.mouse
            x, y = x - 50 - imgui.get_style().indent_spacing * 0.5, context.region.height - y - 129 - 10
            pos = imgui.ImVec2((x, y))
            imgui.set_next_window_pos(pos)
