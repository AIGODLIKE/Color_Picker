import copy
import time

import bpy

from .pref import Color_Picker_Preferences
from .utils import get_brush_color_based_on_mode, get_prefs
from .widget import get_wheeL_tri, color_bar, colorpicker, color_palette, picker_switch_button

from pathlib import Path
from .render import Renderer as BlenderImguiRenderer
from .shader import draw_rec, draw_circle

color_hsv = [0, 0, 0]
color_rgb = [0, 0, 0]
colors = []
color_palette_size = 40
color_palette_dict = {}
# colorbar 颜色拾取处理,拖动bar的最后一个色彩存入colors[0]
color_tmp = []

values = [0.0, 0.60, 0.35, 0.9, 0.70, 0.20, 0.0]
Color_Picker_Imgui_color = (114, 144, 154, 200)
Color_Picker_Imgui_alpha_preview = True
Color_Picker_Imgui_alpha_half_preview = False
Color_Picker_Imgui_drag_and_drop = True
Color_Picker_Imgui_options_menu = True
Color_Picker_Imgui_hdr = False
bl_info = {
    "name": "Color Picker",
    "author": "AIGODLIKE Community:cupcko",
    "version": (1, 0,0),
    "blender": (4, 0, 0),
    "location": "3D View,Image Editor",
    "description": "",
    "category": "color picker"
}


class GlobalImgui:
    _instance = None

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
        """字体"""
        import imgui
        io = imgui.get_io()
        fonts = io.fonts
        fonts_parent = Path(__file__).parent / "AlibabaPuHuiTi-3-35-Thin.ttf"
        fonts.clear()
        fonts.add_font_from_file_ttf(str(fonts_parent), bpy.context.preferences.view.ui_scale * 20,
                                     glyph_ranges_as_int_list=fonts.get_glyph_ranges_chinese_full())

    def init_imgui(self):
        import imgui
        if self.imgui_context is None:
            self.imgui_context = imgui.create_context()
            self.imgui_backend = BlenderImguiRenderer()
            self.imgui_backend.refresh_font_texture_ex()
            self.setup_key_map()

    def shutdown_imgui(self):
        for SpaceType, draw_handler in self.draw_handlers.items():
            SpaceType.draw_handler_remove(draw_handler, 'WINDOW')
        self.draw_handlers.clear()

    def handler_add(self, callback, SpaceType, show_window_pos, verts, ops):
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
            self.draw_handlers[SpaceType] = SpaceType.draw_handler_add(self.draw,
                                                                       (SpaceType, show_window_pos, verts, ops),
                                                                       'WINDOW', 'POST_PIXEL')

        handle = self.next_callback_id
        self.next_callback_id += 1
        self.callbacks[handle] = (callback, SpaceType)
        return handle

    def handler_remove(self, handle):
        # clear all
        if handle not in self.callbacks:
            return
        del self.callbacks[handle]
        if not self.callbacks:
            self.shutdown_imgui()

    def apply_ui_settings(self):
        import imgui
        region = bpy.context.region
        imgui.get_io().display_size = region.width, region.height
        # 圆角控件
        style = imgui.get_style()
        style.window_padding = (1, 1)
        style.window_rounding = 6
        style.frame_rounding = 2
        style.frame_border_size = 1
        # style = imgui.get_current_context().style
        # bg color
        style.set_color_(2, imgui.ImVec4(0, 0, 0, 0.55))

    def draw(self, area, show_window_pos, verts, ops):
        import imgui
        if ops.area!=bpy.context.area:
            return
        a = time.time()
        context = bpy.context
        self.apply_ui_settings()  # 应用用户界面设置

        imgui.new_frame()  # 开始新的 ImGui 帧

        # imgui.get_io().font_default = imgui.get_io().fonts.fonts[1]
        # 定义自定义样式颜色
        title_bg_active_color = imgui.ImVec4(0.546, 0.322, 0.730, 0.9)
        frame_bg_color = imgui.ImVec4(0.512, 0.494, 0.777, 0.573)

        # 将自定义颜色推送到 ImGui 样式堆栈
        imgui.push_style_color(imgui.Col_.frame_bg_active.value, title_bg_active_color)
        imgui.push_style_color(imgui.Col_.frame_bg.value, frame_bg_color)
        imgui.get_style().set_color_(5, imgui.ImVec4(0, 0, 0, 0))
        imgui.push_style_var(20, 1)
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
        if hasattr(ops, 'sv_cursor_pos'):
            if not get_prefs().picker_switch:
                draw_rec(ops.show_window_pos, 71.5, ops.h)
                draw_circle((ops.sv_cursor_pos.x, bpy.context.region.height - ops.sv_cursor_pos.y), ops.sv_cursor_rad / 2,
                            (*get_brush_color_based_on_mode(), 1), (1, 1, 1, .95))

    def setup_key_map(self):
        import imgui
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


def imgui_handler_remove(handle):
    GlobalImgui.get().handler_remove(handle)


class BaseDrawCall:
    # 定义键盘按键映射，键是字符串表示，值是 ImGui 中定义的键码
    import imgui
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

    def init_imgui(self, context):
        if self.area.type=='VIEW_3D':
            self.imgui_handle = GlobalImgui.get().handler_add(self.draw, bpy.types.SpaceView3D, self.show_window_pos,
                                                          self.verts, self)
        elif self.area.type=='IMAGE_EDITOR':
            # context.area=='IMAGE_EDITOR':
            self.imgui_handle = GlobalImgui.get().handler_add(self.draw, bpy.types.SpaceImageEditor, self.show_window_pos,
                                                              self.verts, self)

    def call_shutdown_imgui(self):
        if hasattr(self, 'color_palette'):
            bpy.context.scene['color_picker_col']=self.color_palette
            print("bpy.context.scene['color_picker_col']",bpy.context.scene['color_picker_col'])
        imgui_handler_remove(self.imgui_handle)

    def track_any_cover(self):
        import imgui
        # is_window_hovered 鼠标选中当前窗口的标题栏时触发
        # is_window_focused 当前窗口被聚焦
        # is_item_hovered 当前项(窗口中的)被hover
        # is_item_focused 当前项(窗口中的)被聚焦
        # is_any_item_hovered 有任何项被聚焦
        # hover 不一定 focus,  focus也不一定hover
        self.cover |= imgui.is_any_item_hovered() or imgui.is_window_hovered()

    def poll_mouse(self, context: bpy.types.Context, event: bpy.types.Event):
        import imgui
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
        import imgui
        io = imgui.get_io()  # 获取 ImGui 的 IO 对象

        # 根据事件类型更新 ImGui 的键盘状态
        if event.type in self.key_map:
            io.add_key_event(self.key_map[event.type], event.value == 'PRESS')

        # 处理 Unicode 输入
        if event.unicode and 0 < (char := ord(event.unicode)) < 0x10000:
            io.add_input_character(char)


def convert_color(h, s, v, alpha=255):
    """ Convert HSV to RGBA format and get ImU32 color value. """
    import imgui
    r, g, b = 0.0, .0, .0
    r, g, b = imgui.color_convert_hsv_to_rgb(h, s, v, r, g, b)  # Convert HSV to RGB
    return imgui.get_color_u32(imgui.ImVec4((r * 255), int(g * 255), int(b * 255), alpha))


class Color_Picker_Imgui(bpy.types.Operator, BaseDrawCall):
    bl_idname = "paint.color_picker"
    bl_label = "color picker"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if bpy.context.mode == 'SCULPT' and bpy.context.tool_settings.sculpt.brush == bpy.data.brushes['Paint']:
            sculpt = True
            return sculpt
        if context.area.type == 'IMAGE_EDITOR':
            if context.area.spaces.active.ui_mode=='PAINT':
                image_paint=True
                return image_paint
        if (context.mode in {'PAINT_VERTEX', 'PAINT_TEXTURE', 'PAINT_GPENCIL', 'VERTEX_GPENCIL', }) and context.area.type == 'VIEW_3D':
            return True
        return False



    def draw(self, context: bpy.types.Context):
        import imgui
        a = time.time()
        self.cover = False
        # 展示一个 ImGui 测试窗口
        wf = imgui.WindowFlags_

        window_flags = wf.no_title_bar | wf.no_resize | wf.no_scrollbar | wf.always_auto_resize

        imgui.set_next_window_pos(
            imgui.ImVec2(self.show_window_pos[0] - 127 - imgui.get_style().indent_spacing * 0.5,
                         context.region.height - self.show_window_pos[1] - 129 - 10))
        imgui.begin("Your first window!", True, window_flags)

        # imgui.text("")
        start_pos = imgui.ImVec2(imgui.get_cursor_pos().x, +imgui.get_cursor_pos().y+ 10)
        imgui.set_cursor_pos(start_pos)
        im_cf = imgui.ColorEditFlags_
        if get_prefs().picker_switch:
            picker_type=im_cf.picker_hue_wheel
        else:
            picker_type=im_cf.picker_hue_bar
        misc_flags = picker_type | im_cf.no_options | im_cf.input_rgb | im_cf.no_alpha | im_cf.no_side_preview | im_cf.no_label
        color = get_brush_color_based_on_mode()
        if imgui.is_mouse_clicked(0):
            self.pre_color = copy.deepcopy(color)

        colorpicker_changed, picker_pos, picker_pos2, wheel_center = colorpicker('##aa', color, misc_flags, self)
        imgui.same_line()
        imgui.begin_group()
        global color_hsv, color_rgb, color_tmp, color_palette_dict
        color_bar_changed = color_bar(color, color_hsv, color_rgb, self)
        if imgui.is_mouse_down(0):
            if color_bar_changed:
                color_tmp = copy.deepcopy(color)
            id = imgui.get_current_context().hovered_id
            if hasattr(color_palette_dict, f'c{id}'):
                self.color_palette.insert(0, copy.deepcopy(color_palette_dict[id]))
        elif imgui.is_mouse_released(0):
            if colorpicker_changed:
                self.color_palette.insert(0, copy.deepcopy(color))

        if imgui.is_mouse_released(0):
            if color_tmp != [] and not colorpicker_changed:

                ids = [imgui.get_id(i) for i in ['H ', 'S ', 'V ', 'R ', 'G ', 'B ']]
                if imgui.get_current_context().hovered_id in ids:
                    self.color_palette.insert(0, copy.deepcopy(color_tmp))
        color_palette('##color_palette', color, self.backup_color, self.pre_color, self.color_palette)
        imgui.end_group()
        picker_switch_button(' ##1')
        start_pos = imgui.ImVec2(imgui.get_cursor_pos().x, imgui.get_cursor_pos().y -15)
        imgui.set_cursor_pos(start_pos)
        imgui.text('')
        # imgui.show_demo_window()
        self.track_any_cover()
        if imgui.is_item_hovered():
            imgui.set_keyboard_focus_here(-1)

        imgui.end()


    def invoke(self, context, event):
        self.cover = False
        self.show_window_pos = (event.mouse_region_x, event.mouse_region_y)
        self.show_window_imgui = False
        self.verts = get_wheeL_tri(self.show_window_pos)
        self.backup_color = copy.deepcopy(get_brush_color_based_on_mode())
        self.area=context.area
        self.pre_color = copy.deepcopy(self.backup_color)
        global colors, color_palette_size
        if len(colors) > color_palette_size:
            del colors[color_palette_size:]
        try:
            self.color_palette=[list(c) for c in bpy.context.scene['color_picker_col']]
        except:
            self.color_palette = colors
        self.init_imgui(context)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}
    def refresh(self):
        for area in bpy.context.screen.areas:
            if area.type in ['VIEW_3D','IMAGE_EDITOR']:
                area.tag_redraw()
    def modal(self, context, event):
        if event.type == 'SPACE' and event.value == 'RELEASE':
            self.call_shutdown_imgui()
            self.refresh()
            return {'FINISHED'}
        if event.type == 'Z' and event.value == 'RELEASE':
            self.call_shutdown_imgui()
            self.refresh()
            return {'FINISHED'}
        a = time.time()
        if context.area:
            context.area.tag_redraw()
        else:
            self.call_shutdown_imgui()
            self.refresh()
            return {'FINISHED'}
        # 鼠标不在 region 范围则不更新
        self.mpos = event.mouse_region_x, event.mouse_region_y
        w, h = context.region.width, context.region.height
        if 0 > self.mpos[0] or self.mpos[0] > w or 0 > self.mpos[1] or self.mpos[1] > h:
            # print('PASS_THROUGH')
            return {"PASS_THROUGH"}
        if event.type in {"ESC",'WINDOW_DEACTIVATE'}:
            self.call_shutdown_imgui()
            self.refresh()
            return {'FINISHED'}
        if event.type in {'RIGHTMOUSE'}:
            self.call_shutdown_imgui()
            self.refresh()
            return {'FINISHED'}
        if event.type == 'X' and event.value == 'RELEASE':
            from .utils import exchange_brush_color_based_on_mode
            exchange_brush_color_based_on_mode(exchange=True)

        if context.region:
            region = context.region
        else:
            self.call_shutdown_imgui()
            self.refresh()
            return {'FINISHED'}
        self.poll_mouse(context, event)
        if not self.cover:
            return {"PASS_THROUGH"}
        self.poll_events(context, event)

        return {"RUNNING_MODAL"}



class TranslationHelper():
    def __init__(self, name: str, data: dict, lang='zh_CN'):
        self.name = name
        self.translations_dict = dict()

        for src, src_trans in data.items():
            key = ("Operator", src)
            self.translations_dict.setdefault(lang, {})[key] = src_trans
            key = ("*", src)
            self.translations_dict.setdefault(lang, {})[key] = src_trans

    def register(self):
        try:
            bpy.app.translations.register(self.name, self.translations_dict)
        except(ValueError):
            pass

    def unregister(self):
        bpy.app.translations.unregister(self.name)


from . import zh_CN

Colorpickerzh_CN = TranslationHelper('Colorpickerzh_CN', zh_CN.data)
Colorpickerzh_HANS = TranslationHelper('Colorpickerzh_HANS', zh_CN.data, lang='zh_HANS')

from .utils import register_keymaps,unregister_keymaps
from .keymap import keys
def register():
    if bpy.app.version < (4, 0, 0):
        Colorpickerzh_CN.register()
    else:
        Colorpickerzh_CN.register()
        Colorpickerzh_HANS.register()
    bpy.utils.register_class(Color_Picker_Imgui)
    bpy.utils.register_class(Color_Picker_Preferences)
    global keymaps
    keymaps = register_keymaps(keys['COLOR_PICKER'])


def unregister():
    if bpy.app.version < (4, 0, 0):
        Colorpickerzh_CN.unregister()
    else:
        Colorpickerzh_CN.unregister()
        Colorpickerzh_HANS.unregister()
    bpy.utils.unregister_class(Color_Picker_Imgui)
    bpy.utils.unregister_class(Color_Picker_Preferences)
    global keymaps
    if keymaps:
        unregister_keymaps(keymaps)


if __name__ == "__main__":
    register()
