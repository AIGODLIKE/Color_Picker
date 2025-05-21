import bpy
from mathutils import Vector

from .color_picker import ImguiColorPicker
from .event_handle import ImguiEvent
from .key import SyncKey


class ColorPicker(bpy.types.Operator, ImguiEvent, SyncKey, ImguiColorPicker):
    bl_idname = "paint.color_picker"
    bl_label = "Color picker"
    bl_options = {'REGISTER', 'UNDO'}

    timer = None
    mouse: Vector = None

    def invoke(self, context, event):
        self.register_imgui()

        self.timer = context.window_manager.event_timer_add(1 / 60, window=context.window)
        self.mouse = Vector((event.mouse_region_x, event.mouse_region_y))

        self.sync_key(context, event)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        self.sync_key(context, event)
        if not context.area:
            self.exit(context)
            return {"CANCELLED"}
        x, y = self.mouse = Vector((event.mouse_region_x, event.mouse_region_y))
        w, h = context.region.width, context.region.height

        if 0 > x or x > w or 0 > y or y > h:
            # 鼠标不在 region 范围则不更新
            return {"PASS_THROUGH"}
        context.area.tag_redraw()

        if event.type == "ESC":
            self.exit(context)
            return {"FINISHED"}

        return {"RUNNING_MODAL"}

    def execute(self, context):
        return {"FINISHED"}

    def exit(self, context):
        self.unregister_imgui()


def register():
    bpy.utils.register_class(ColorPicker)


def unregister():
    bpy.utils.unregister_class(ColorPicker)
