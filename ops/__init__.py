import bpy


class ColorPicker(bpy.types.Operator):
    bl_idname = "paint.color_picker"
    bl_label = "Color picker"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        return {"FINISHED"}

    def execute(self, context, event):
        return {"FINISHED"}


def register():
    bpy.utils.register_class(ColorPicker)


def unregister():
    bpy.utils.unregister_class(ColorPicker)
