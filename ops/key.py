import bpy


class SyncKey:

    def sync_key(self, context: bpy.types.Context, event: bpy.types.Event):
        from imgui_bundle import imgui
        io = imgui.get_io()

        event_type = event.type
        is_press = event.value == 'PRESS'

        # 鼠标 mouse
        x, y = (self.mouse[0], context.region.height - 1 - self.mouse[1])
        io.add_mouse_pos_event(x, y)

        if event_type == 'LEFTMOUSE':
            io.add_mouse_button_event(0, is_press)
        elif event_type == 'RIGHTMOUSE':
            io.add_mouse_button_event(1, is_press)
        elif event_type == 'MIDDLEMOUSE':
            io.add_mouse_button_event(2, is_press)
        if event_type == 'WHEELUPMOUSE':
            io.add_mouse_wheel_event(0, 1)
        elif event_type == 'WHEELDOWNMOUSE':
            io.add_mouse_wheel_event(0, -1)

        # 处理 Unicode 输入
        if event.unicode and 0 < (char := ord(event.unicode)) < 0x10000:
            io.add_input_character(char)
        self.sync_keyboard(event)

    @staticmethod
    def sync_keyboard(event):
        from imgui_bundle import imgui

        io = imgui.get_io()

        event_type = event.type
        is_press = event.value == 'PRESS'

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
            'LEFT_CTRL': imgui.Key.right_ctrl,
            'RIGHT_CTRL': imgui.Key.left_ctrl,
            'LEFT_ALT': imgui.Key.left_alt,
            'RIGHT_ALT': imgui.Key.right_alt,
            'LEFT_SHIFT': imgui.Key.left_shift,
            'RIGHT_SHIFT': imgui.Key.right_shift,
            'OSKEY': imgui.Key.comma,
        }

        # 根据事件类型更新 ImGui 的键盘状态
        if event_type in key_map:
            k = key_map[event_type]
            io.add_key_event(k, is_press)
            # io.add_input_character(k)
