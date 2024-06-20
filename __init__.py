# import imgui
import math

from mathutils import Vector
import time

from .utils import get_imgui_widget_center

color_picker_color = (114, 144, 154, 200)
color_picker_alpha_preview = True
color_picker_alpha_half_preview = False
color_picker_drag_and_drop = True
color_picker_options_menu = True
color_picker_hdr = False
bl_info = {
    "name": "imguitest",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "everywhere",
    "description": "Description of your plugin",
    "category": "Object"
}

import bpy
from .extern.imgui_bundle import imgui
# import imgui
from pathlib import Path
from gpu_extras.presets import draw_texture_2d
from .render import Renderer as BlenderImguiRenderer
from .shader import draw_rec


class GlobalImgui:
    _instance = None

    # def __init__(self):
    #     self.imgui_context = None

    def __init__(self):
        self.imgui_context = None
        self.imgui_backend = None
        self.draw_handlers = {}
        self.callbacks = {}
        self.next_callback_id = 0

    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = GlobalImgui()
        return cls._instance

    @staticmethod
    def init_font():
        '''字体'''
        io = imgui.get_io()
        fonts = io.fonts
        fonts_parent = Path(__file__).parent / "bmonofont-i18n.ttf"
        fonts.clear()
        fonts.add_font_from_file_ttf(str(fonts_parent), bpy.context.preferences.view.ui_scale * 20,
                                     glyph_ranges_as_int_list=fonts.get_glyph_ranges_chinese_full())

    def init_imgui(self):
        if self.imgui_context is None:
            self.imgui_context = imgui.create_context()
            self.imgui_backend = BlenderImguiRenderer()
            self.imgui_backend.refresh_font_texture_ex()
            self.setup_key_map()
            print('初始化imgui')

    # def init_imgui(self):
    #     if self.imgui_context:
    #         return
    #     self.imgui_context = imgui.create_context()
    #     # self.init_font()
    #     self.imgui_backend = BlenderImguiRenderer()
    #     self.imgui_backend.refresh_font_texture_ex()
    #     self.setup_key_map()
    #
    #     self.draw_handlers = {}
    #     self.callbacks = {}
    #     self.next_callback_id = 0
    # print(f'next_callback_id,{self.next_callback_id} ')
    # print('初始化imgui')

    def shutdown_imgui(self):
        # print('self.draw_handlers.items()',self.draw_handlers.items())
        for SpaceType, draw_handler in self.draw_handlers.items():
            SpaceType.draw_handler_remove(draw_handler, 'WINDOW')
        self.draw_handlers.clear()
        # imgui.destroy_context(self.imgui_context)
        # self.imgui_context = None

        # print('关闭imgui,移除句柄',self.draw_handlers.items())

    def handler_add(self, callback, SpaceType, show_window_pos):
        """
        @param callback The draw function to add
        @param SpaceType Can be any class deriving from bpy.types.Space
        @return An identifing handle that must be provided to handler_remove in
                order to remove this callback.
        """
        a = time.time()
        if self.imgui_context is None:
            self.init_imgui()
        # print(self.draw_handlers)
        if SpaceType not in self.draw_handlers:
            self.draw_handlers[SpaceType] = SpaceType.draw_handler_add(self.draw, (SpaceType, show_window_pos),
                                                                       'WINDOW', 'POST_PIXEL')
            # print('添加句柄,绘制回调,开始帧')
        # print(f'next_callback_id,{self.next_callback_id} ')
        handle = self.next_callback_id
        # print(f'next_callback_id,{self.next_callback_id} ,handle {handle}')
        self.next_callback_id += 1
        # print(f'next_callback_id,{self.next_callback_id} ,handle {handle}')
        # self.callbacks[handle] = (callback, SpaceType)
        self.callbacks[handle] = (callback, SpaceType)
        # print('hand add', time.time() - a)
        return handle

    def handler_remove(self, handle):
        # print( handle, self.draw_handlers.items())
        # clear all
        if handle not in self.callbacks:
            # print(f"Error: invalid imgui callback handle: {handle}")
            return
        del self.callbacks[handle]
        # print('self.callbacks',self.callbacks.items())
        if not self.callbacks:
            self.shutdown_imgui()
        # print('self.draw_handlers.items()',self.draw_handlers.items())

    def apply_ui_settings(self):
        region = bpy.context.region
        imgui.get_io().display_size = region.width, region.height
        # 圆角控件
        style = imgui.get_style()
        style.window_padding = (1, 1)
        style.window_rounding = 2
        style.frame_rounding = 2
        style.frame_border_size = 1

    def draw(self, area, show_window_pos):
        a = time.time()
        context = bpy.context
        self.apply_ui_settings()  # 应用用户界面设置

        imgui.new_frame()  # 开始新的 ImGui 帧
        # 定义自定义样式颜色
        title_bg_active_color = imgui.ImVec4(0.546, 0.322, 0.730, 0.9)
        frame_bg_color = imgui.ImVec4(0.512, 0.494, 0.777, 0.573)

        # 将自定义颜色推送到 ImGui 样式堆栈
        imgui.push_style_color(imgui.Col_.frame_bg_active.value, title_bg_active_color)
        imgui.push_style_color(imgui.Col_.frame_bg.value, frame_bg_color)
        imgui.get_style().set_color_(5, imgui.ImVec4(0, 0, 0, 0))
        imgui.push_style_var(20, 3)
        invalid_callback = []  # 创建一个列表来存储无效的回调函数

        for cb, SpaceType in self.callbacks.values():
            if SpaceType == area:
                cb(bpy.context)
        # 从 ImGui 样式堆栈中弹出自定义颜色
        imgui.pop_style_color()
        imgui.pop_style_color()
        imgui.pop_style_var(1)
        imgui.end_frame()  # 结束 ImGui 帧
        imgui.render()  # 渲染 ImGui 绘制数据

        # 使用自定义渲染器渲染 ImGui 绘制数据
        self.imgui_backend.render(imgui.get_draw_data())
        color = context.tool_settings.vertex_paint.brush.color
        p = imgui.get_mouse_pos()

        # draw_rec(show_window_pos, 116, float(color[0]))
        # print('global',time.time() - a)

    def setup_key_map(self):
        io = imgui.get_io()
        keys = (
            imgui.Key.tab,
            imgui.Key.left_arrow,
            imgui.Key.right_arrow,
            imgui.Key.up_arrow,
            imgui.Key.down_arrow,
            imgui.Key.home,
            imgui.Key.end,
            imgui.Key.insert,
            imgui.Key.delete,
            imgui.Key.backspace,
            imgui.Key.enter,
            imgui.Key.escape,
            imgui.Key.page_up,
            imgui.Key.page_down,
            imgui.Key.a,
            imgui.Key.c,
            imgui.Key.v,
            imgui.Key.x,
            imgui.Key.y,
            imgui.Key.z,
        )
        for k in keys:
            # We don't directly bind Blender's event type identifiers
            # because imgui requires the key_map to contain integers only
            io.add_input_character(k)
            # io.key_mods[k] = k


def inbox(x, y, w, h, mpos):
    if (x < mpos[0] < x + w) and (y - h < mpos[1] < y):
        return True
    return False


def imgui_handler_add(callback, SpaceType, show_window_pos):
    return GlobalImgui.get().handler_add(callback, SpaceType, show_window_pos)


def imgui_handler_remove(handle):
    GlobalImgui.get().handler_remove(handle)


class BaseDrawCall:
    # 定义键盘按键映射，键是字符串表示，值是 ImGui 中定义的键码
    key_map = {
        'TAB': imgui.Key.tab,
        'LEFT_ARROW': imgui.Key.left_arrow,
        'RIGHT_ARROW': imgui.Key.right_arrow,
        'UP_ARROW': imgui.Key.up_arrow,
        'DOWN_ARROW': imgui.Key.down_arrow,
        'HOME': imgui.Key.home,
        'END': imgui.Key.end,
        'INSERT': imgui.Key.insert,
        'DEL': imgui.Key.delete,
        'BACK_SPACE': imgui.Key.backspace,
        'SPACE': imgui.Key.space,
        'RET': imgui.Key.enter,
        'ESC': imgui.Key.escape,
        'PAGE_UP': imgui.Key.page_up,
        'PAGE_DOWN': imgui.Key.page_down,
        'A': imgui.Key.a,
        'C': imgui.Key.c,
        'V': imgui.Key.v,
        'X': imgui.Key.x,
        'Y': imgui.Key.y,
        'Z': imgui.Key.z,
        'LEFT_CTRL': imgui.Key.im_gui_mod_ctrl,
        'RIGHT_CTRL': imgui.Key.im_gui_mod_ctrl,
        'LEFT_ALT': imgui.Key.im_gui_mod_alt,
        'RIGHT_ALT': imgui.Key.im_gui_mod_alt,
        'LEFT_SHIFT': imgui.Key.im_gui_mod_shift,
        'RIGHT_SHIFT': imgui.Key.im_gui_mod_shift,
        'OSKEY': imgui.Key.comma,
    }

    def __init__(self):
        self.c = .0
        self.mpos = (0, 0)  # 初始化鼠标位置

    def draw(self, context):
        pass

    def init_imgui(self, contxt):
        self.imgui_handle = imgui_handler_add(self.draw, bpy.types.SpaceView3D, self.show_window_pos)
        # self.imgui_handle=GlobalImgui.get().handler_add(self.draw,bpy.types.SpaceView3D)

    def call_shutdown_imgui(self):
        # print('self.imgui handle',self.imgui_handle)
        imgui_handler_remove(self.imgui_handle)
        # GlobalImgui().handler_remove(self.imgui_handle)

    def track_any_cover(self):
        # is_window_hovered 鼠标选中当前窗口的标题栏时触发
        # is_window_focused 当前窗口被聚焦
        # is_item_hovered 当前项(窗口中的)被hover
        # is_item_focused 当前项(窗口中的)被聚焦
        # is_any_item_hovered 有任何项被聚焦
        # hover 不一定 focus,  focus也不一定hover
        self.cover |= imgui.is_any_item_hovered() or imgui.is_window_hovered()
        # print(imgui.is_any_item_hovered() , imgui.is_window_hovered())

    # def clear(self):
    #     # 移除绘制处理器
    #     GlobalImgui().get().handler_remove(self.draw_call)
    #     print(GlobalImgui().get().callbacks)

    def poll_mouse(self, context: bpy.types.Context, event: bpy.types.Event):
        io = imgui.get_io()  # 获取 ImGui 的 IO 对象
        # 将 Blender 的鼠标位置转换为 ImGui 的坐标系
        io.add_mouse_pos_event(self.mpos[0], context.region.height - 1 - self.mpos[1])
        # 根据事件类型更新 ImGui 的鼠标状态
        if event.type == 'LEFTMOUSE':
            io.add_mouse_button_event(0, event.value == 'PRESS')
        elif event.type == 'RIGHTMOUSE':
            io.add_mouse_button_event(1, event.value == 'PRESS')
        elif event.type == 'MIDDLEMOUSE':
            io.add_mouse_button_event(2, event.value == 'PRESS')
        if event.type == 'WHEELUPMOUSE':
            io.add_mouse_wheel_event(0, 1)
        elif event.type == 'WHEELDOWNMOUSE':
            io.add_mouse_wheel_event(0, -1)

    def poll_events(self, context: bpy.types.Context, event: bpy.types.Event):
        io = imgui.get_io()  # 获取 ImGui 的 IO 对象

        # 根据事件类型更新 ImGui 的键盘状态
        if event.type in self.key_map:
            io.add_key_event(self.key_map[event.type], event.value == 'PRESS')

        # 处理 Unicode 输入
        if event.unicode and 0 < (char := ord(event.unicode)) < 0x10000:
            io.add_input_character(char)

def convert_color(h, s, v, alpha=255):
    """ Convert HSV to RGBA format and get ImU32 color value. """
    r, g, b = 0.0, .0, .0
    r, g, b = imgui.color_convert_hsv_to_rgb(h, s, v, r, g, b)  # Convert HSV to RGB
    return imgui.get_color_u32(imgui.ImVec4((r * 255), int(g * 255), int(b * 255), alpha))



class ImguiGuiTest(bpy.types.Operator, BaseDrawCall):
    bl_idname = "imgui.gui_test"
    bl_label = "Gui Test"

    def draw(self, context: bpy.types.Context):
        a = time.time()
        self.cover = False
        # 展示一个 ImGui 测试窗口

        wf = imgui.WindowFlags_
        # window_flags=wf.no_title_bar|wf.no_resize|wf.no_scrollbar|wf.always_auto_resize
        window_flags = wf.no_title_bar | wf.no_resize | wf.no_scrollbar|wf.always_auto_resize
        # window_flags = 0
        # imgui.set_next_window_size(imgui.ImVec2(570,240))
        # if not self.show_window_imgui:
        imgui.set_next_window_pos(
            imgui.ImVec2(self.show_window_pos[0] - 117, context.region.height - self.show_window_pos[1] - 117))
        #     self.show_window_imgui = True
        # print('imgui mouse', imgui.get_mouse_pos(), imgui.get_window_size())
        imgui.begin("Your first window!", True, window_flags)
        # imgui.text("Hello world!")
        # imgui.text("Another line!")
        imgui.text("")
        # imgui.ColorEditFlags_.picker_hue_wheel
        misc_flags = imgui.ColorEditFlags_.picker_hue_wheel | imgui.ColorEditFlags_.no_options | imgui.ColorEditFlags_.no_inputs | imgui.ColorEditFlags_.no_alpha | imgui.ColorEditFlags_.no_side_preview | imgui.ColorEditFlags_.no_label
        # imgui.get_window_draw_list().
        # imgui.text("Color button only:")
        # p3 = imgui.get_cursor_screen_pos()
        # print(p3)
        # imgui.set_next_item_width(254)
        # changed1, self.color4 = imgui.color_picker4("MyColor", imgui.ImVec4(self.color4), misc_flags)  # type: ignore
        from .widget import colorpicker
        changed1=colorpicker('aa',self.color4,misc_flags)
        # print(333, self.color4[0], self.color4[1], self.color4[2])
        # print('hei', imgui.get_frame_height())
        # imgui.same_line()
        # changed2, self.color4=imgui.color_edit4("##RefColor",self.color4, misc_flags)
        # changed1, self.color4=imgui.color_picker4("MyColor", imgui.ImVec4(self.color4), misc_flags )  # type: ignore
        # square_sz = imgui.get_frame_height()
        # bars_width = square_sz
        # width = imgui.calc_item_width()
        # window = imgui.internal.get_current_window()
        # picker_pos = window.dc.cursor_pos
        # sv_picker_size = max(bars_width * 1, width - (
        #         bars_width + imgui.get_style().item_inner_spacing.x))
        # wheel_thickness = sv_picker_size * 0.08
        # wheel_r_outer = sv_picker_size * 0.50
        # wheel_r_inner = wheel_r_outer - wheel_thickness
        # wheel_center = imgui.ImVec2(picker_pos.x + (sv_picker_size + bars_width) * 0.5,
        #                             picker_pos.y + sv_picker_size * 0.5)
        # aeps = 0.5 / wheel_r_outer
        # Define colors using HSV values and convert them to ImU32
        col_a = convert_color(0, 0.0, 1.0)  # White: H = 0, S = 0%, V = 100%
        col_b = convert_color(0, 1.0, 1.0)  # Red: H = 0, S = 100%, V = 100%
        col_c = convert_color(0, 1.0, 1.0)  # Green: H = 120°, S = 100%, V = 100%
        col_d = convert_color(0, 0.0, 1.0)  # Black: H = 0, S = 0%, V = 0%

        # imgui.get_window_draw_list().add_rect_filled_multi_color(imgui.ImVec2(p0[0], p0[1]), imgui.ImVec2(p1[0], p1[1]),
        #                                                          col_a, col_b, col_c, col_d)
        # imgui.get_window_draw_list().add_triangle_filled(imgui.ImVec2(p1[0],p0[1]),imgui.ImVec2(p1[0], p1[1]),imgui.ImVec2(p1[0]-1.732050807*gradient_size[0]/2, p0[1]+gradient_size[0]/2),col_b)
        # imgui.invisible_button("##gradient2", imgui.ImVec2(gradient_size[0], gradient_size[0]))
        # imgui.ImDrawList.add_triangle()
        imgui.same_line()
        values = [0.0, 0.60, 0.35, 0.9, 0.70, 0.20, 0.0]
        imgui.push_id('set')
        lines = ['H', 'S', 'V', 'R', 'G', 'B']
        imgui.begin_group()
        for i in range(6):
            imgui.set_next_item_width(256)
            imgui.push_style_color(imgui.Col_.frame_bg, imgui.ImVec4(1 / 7.0, 0.6, 1, 0))
            imgui.push_style_color(imgui.Col_.frame_bg_hovered, imgui.ImVec4(1 / 7.0, .7, 1, 0))
            imgui.push_style_color(imgui.Col_.frame_bg_active, imgui.ImVec4(1 / 7.0, .8, 1, 0))
            imgui.push_style_color(imgui.Col_.slider_grab, imgui.ImVec4(1 / 7.0, 0.5, 1, 1))
            # imgui.push_style_color(imgui.Col_.border,imgui.ImVec4(1/7.0, 1, 1,0))
            gradient_size = [imgui.calc_item_width(), imgui.get_frame_height()]

            p0 = imgui.get_cursor_screen_pos()

            p1 = (p0.x + gradient_size[0], p0.y + gradient_size[1])
            imgui.get_window_draw_list().add_rect_filled_multi_color(imgui.ImVec2(p0[0] + 2, p0[1]),
                                                                     imgui.ImVec2(p1[0] - 2, p1[1]),
                                                                     imgui.get_color_u32(
                                                                         imgui.ImVec4(255, 255, 255, 1)),
                                                                     imgui.get_color_u32(imgui.ImVec4(255, 0, 0, 1)),
                                                                     imgui.get_color_u32(imgui.ImVec4(255, 0, 0, 1)),
                                                                     imgui.get_color_u32(imgui.ImVec4(255, 255, 255, 1))
                                                                     )
            changed, self.c = imgui.slider_float(lines[i], values[i], 0.0, 1.0, "")

            if imgui.is_item_active() or imgui.is_item_hovered():
                imgui.set_tooltip(f'{self.c:.3f}')
            imgui.pop_style_color(4)
        imgui.end_group()

        imgui.pop_id()

        # imgui.show_demo_window()

        self.track_any_cover()
        if imgui.is_item_hovered():
            imgui.set_keyboard_focus_here(-1)

        imgui.end()

        # print('draw',time.time() - a)

    def invoke(self, context, event):
        a = time.time()
        origin = Vector((event.mouse_region_x, event.mouse_region_y))
        self.color = [1., .5, 0.]
        self.color4 = [1., .5, 0.0, 0.5]
        self.cover = False
        # p = imgui.get_mouse_pos()
        self.show_window_pos = (event.mouse_region_x, event.mouse_region_y)
        self.show_window_imgui = False
        self.message = "Type something here!"
        self.init_imgui(context)

        # if not self.try_reg(self.area, context, origin):
        #     return {"FINISHED"}
        context.window_manager.modal_handler_add(self)
        # print('预处理数据')
        # print(time.time() - a)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'SPACE' and event.value == 'RELEASE':
            self.call_shutdown_imgui()
            return {'FINISHED'}
        a = time.time()
        if context.area:
            context.area.tag_redraw()
        else:
            self.call_shutdown_imgui()
            return {'FINISHED'}
        # print('1')
        # 鼠标不在 region 范围则不更新
        self.mpos = event.mouse_region_x, event.mouse_region_y
        # print('mouse', self.mpos)
        # print('mouse', context.area.height)
        w, h = context.region.width, context.region.height
        if 0 > self.mpos[0] or self.mpos[0] > w or 0 > self.mpos[1] or self.mpos[1] > h:
            return {"PASS_THROUGH"}
        # print('2')

        if event.type in {"ESC"}:
            self.call_shutdown_imgui()
            return {'FINISHED'}
        # print('3')
        if event.type in {'RIGHTMOUSE'}:
            self.call_shutdown_imgui()
            return {'FINISHED'}
        # print('4')
        if context.region:

            region = context.region
        else:
            self.call_shutdown_imgui()
            return {'FINISHED'}
        # print('5')
        self.poll_mouse(context, event)
        # print(context.area, self.mpos, self.cover, imgui.is_any_item_focused())
        # print('6')
        if not self.cover:
            return {"PASS_THROUGH"}
        # print('1')
        self.poll_events(context, event)

        return {"RUNNING_MODAL"}


def register_keymaps():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View Generic', space_type='VIEW_3D', region_type='WINDOW')
        kmi = km.keymap_items.new(ImguiGuiTest.bl_idname, 'SPACE', 'PRESS')
        return km, kmi


def unregister_keymaps(km, kmi):
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km.keymap_items.remove(kmi)
        wm.keyconfigs.addon.keymaps.remove(km)


def register():
    bpy.utils.register_class(ImguiGuiTest)
    # bpy.utils.register_class(ImGuiGPUOperator)
    global keymap
    keymap = register_keymaps()


def unregister():
    bpy.utils.unregister_class(ImguiGuiTest)
    # bpy.utils.unregister_class(ImGuiGPUOperator)
    global keymap
    if keymap:
        unregister_keymaps(*keymap)


if __name__ == "__main__":
    register()
