import bpy
from mathutils import Vector

from .color_sync import ColorSync
from .color_widget import ColorWidget
from .demo import Demo
from .draw import Draw
from .event_handle import ImguiEvent
from .key import SyncKey
from ..utils import get_brush


class ColorPicker(bpy.types.Operator, ImguiEvent, SyncKey, ColorSync, ColorWidget, Draw, Demo):
    bl_idname = "paint.color_picker"
    bl_label = "Color picker"
    bl_options = {'REGISTER', 'UNDO'}

    timer = None
    mouse: Vector = None
    start_color = None
    start_hsv = None

    @classmethod
    def poll(cls, context):
        have_brush = get_brush(context) is not None
        is_3d_view = context.space_data and context.space_data.type == "VIEW_3D"
        is_edit_image = context.space_data and context.space_data.type == "IMAGE_EDITOR"
        # print(have_brush, context.space_data.type, is_3d_view)
        return have_brush and (is_3d_view or is_edit_image)

    def init_color(self, context):
        self.start_color = self.get_color(context)
        if self.start_color is None:
            self.report({'ERROR'}, "Not Fond Color!!!")
            return {"CANCELLED"}
        self.start_hsv = self.start_color.hsv
        return None

    def invoke(self, context, event):
        if init := self.init_color(context):
            return init

        self.timer = context.window_manager.event_timer_add(1 / 60, window=context.window)
        self.mouse = Vector((event.mouse_region_x, event.mouse_region_y))

        self.register_imgui(context)
        self.sync_key(context, event)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        self.mouse = Vector((event.mouse_region_x, event.mouse_region_y))

        if not context.area:
            self.exit(context)
            return {"CANCELLED"}

        if event.type in ("ESC", "RIGHTMOUSE"):
            self.exit(context)
            return {"FINISHED"}
        # elif event.type in {"SPACE", "E"} and event.value == "RELEASE":
        #     self.exit(context)
        #     return {"FINISHED"}

        self.sync_key(context, event)
        self.refresh(context)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        return {"FINISHED"}

    def exit(self, context):
        self.unregister_imgui(context)
        self.refresh(context)

    @staticmethod
    def refresh(context):
        for area in context.screen.areas:
            area.tag_redraw()



def register():
    bpy.utils.register_class(ColorPicker)


def unregister():
    bpy.utils.unregister_class(ColorPicker)
