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
        self.create_context(context)
        space = context.space_data.bl_rna.type_recast()
        self.handler = space.draw_handler_add(self.draw_imgui, (context,), 'WINDOW', 'POST_PIXEL')
        self.draw_error = False
        self.window_position = None

    def unregister_imgui(self, context):
        context.space_data.bl_rna.type_recast().draw_handler_remove(self.handler, 'WINDOW')

    def create_context(self, context):
        from .render import Renderer
        import imgui
        if self.imgui_context is None:
            self.imgui_context = imgui.create_context()
            self.imgui_backend = Renderer()
            self.imgui_backend.refresh_font_texture_ex()
