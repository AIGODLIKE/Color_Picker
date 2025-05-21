import bpy


class ImguiEvent:
    handler = None

    # imgui
    io = None  # imgui.core._IO
    imgui_context = None  # imgui.core._ImGuiContext
    imgui_backend = None
    draw_error = None

    def register_imgui(self):
        import imgui
        self.create_context()
        self.io = imgui.get_io()
        self.handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_imgui, (), 'WINDOW', 'POST_PIXEL')
        self.draw_error = False

    def unregister_imgui(self):
        bpy.types.SpaceView3D.draw_handler_remove(self.handler, 'WINDOW')

    def create_context(self):
        from .renderer import BlenderImguiRenderer
        import imgui
        if self.imgui_context is None:
            self.imgui_context = imgui.create_context()
            self.imgui_backend = BlenderImguiRenderer()
            self.imgui_backend.refresh_font_texture_ex()

    def draw_imgui(self):
        import imgui
        try:
            if self.draw_error:
                return
            self.create_context()
            context = bpy.context
            imgui.get_io().display_size = (context.region.width, context.region.height)

            imgui.new_frame()
            self.start_window(context)

            imgui.text("Hello world!")

            # self.draw_color_picker()
            imgui.show_test_window()

            imgui.end()
            imgui.end_frame()
            imgui.render()
            self.imgui_backend.render(imgui.get_draw_data())
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.draw_error = True

    def start_window(self, context):
        import imgui

        x, y = self.mouse
        x, y = x - 127 - imgui.get_style().indent_spacing * 0.5, context.region.height - y - 129 - 10
        imgui.set_next_window_position(x, y)

        window_flags = (
                imgui.WINDOW_NO_TITLE_BAR |
                imgui.WINDOW_NO_RESIZE |
                imgui.WINDOW_NO_SCROLLBAR |
                imgui.WINDOW_ALWAYS_AUTO_RESIZE
        )
        imgui.begin("Window", False, window_flags)

        start_pos = imgui.Vec2(imgui.get_cursor_pos().x, +imgui.get_cursor_pos().y + 10)
        imgui.set_cursor_pos(start_pos)
