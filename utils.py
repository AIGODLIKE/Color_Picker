from .extern.imgui_bundle import imgui
def get_imgui_widget_center():
    h=116
    return imgui.ImVec2(imgui.get_mouse_pos().x-h,imgui.get_mouse_pos().y-h)