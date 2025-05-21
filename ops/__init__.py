
def register():
    bpy.utils.register_class(Color_Picker_Imgui)
    bpy.utils.register_class(Color_Picker_Preferences)


def unregister():
    bpy.utils.unregister_class(Color_Picker_Imgui)
    bpy.utils.unregister_class(Color_Picker_Preferences)