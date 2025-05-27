import bpy
from mathutils import Vector

from .draw import Draw
from .color_sync import ColorSync
from .color_widget import ColorWidget
from .event_handle import ImguiEvent
from .key import SyncKey


class ColorPicker(bpy.types.Operator, ImguiEvent, SyncKey, ColorSync, ColorWidget, Draw):
    bl_idname = "paint.color_picker"
    bl_label = "Color picker"
    bl_options = {'REGISTER', 'UNDO'}

    timer = None
    mouse: Vector = None
    start_color = None
    start_hsv = None

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
        # elif self.check_region(context, event):
        #     return {"PASS_THROUGH"}

        if event.type in ("ESC", "RIGHTMOUSE"):
            self.exit(context)
            return {"FINISHED"}
        self.sync_key(context, event)
        context.area.tag_redraw()
        return {"RUNNING_MODAL"}

    def execute(self, context):
        return {"FINISHED"}

    def exit(self, context):
        self.unregister_imgui()
        context.area.tag_redraw()

    def check_region(self, context, event):
        """
        鼠标不在 region 范围则不更新
        """

        x, y = self.mouse
        w, h = context.region.width, context.region.height

        if 0 > x or x > w or 0 > y or y > h:
            return True


def register():
    bpy.utils.register_class(ColorPicker)


def unregister():
    bpy.utils.unregister_class(ColorPicker)
