import bpy


class SyncKey:

    def sync_key(self, context: bpy.types.Context, event: bpy.types.Event):
        import imgui
        io: "imgui.core._IO" = imgui.get_io()

        event_type = event.type
        is_press = event.value == 'PRESS'
        # 鼠标 mouse
        x, y = (self.mouse[0], context.region.height - 1 - self.mouse[1])
        io.mouse_pos = (x, y)

        if event_type == 'LEFTMOUSE':
            io.mouse_down[0] = is_press
            if not is_press:
                self.add_palettes_color(context, self.start_color)
        elif event_type == 'RIGHTMOUSE':
            io.mouse_down[1] = is_press
        elif event_type == 'MIDDLEMOUSE':
            io.mouse_down[2] = is_press
        elif event_type == 'WHEELUPMOUSE':
            io.mouse_wheel = 1
        elif event_type == 'WHEELDOWNMOUSE':
            io.mouse_wheel = -1
        elif event_type == "F12" and is_press:
            self.show_test = not self.show_test

        # 处理 Unicode 输入
        if event.unicode and 0 < (char := ord(event.unicode)) < 0x10000:
            io.add_input_character(char)
        self.sync_keyboard(event)

    @staticmethod
    def sync_keyboard(event):
        import imgui

        io = imgui.get_io()

        event_type = event.type
        is_press = event.value == 'PRESS'

        key_map = {
            'TAB': imgui.KEY_TAB,
            'LEFT_ARROW': imgui.KEY_LEFT_ARROW,
            'RIGHT_ARROW': imgui.KEY_RIGHT_ARROW,
            'UP_ARROW': imgui.KEY_UP_ARROW,
            'DOWN_ARROW': imgui.KEY_DOWN_ARROW,
            'HOME': imgui.KEY_HOME,
            'END': imgui.KEY_END,
            'INSERT': imgui.KEY_INSERT,
            'DEL': imgui.KEY_DELETE,
            'BACK_SPACE': imgui.KEY_BACKSPACE,
            'SPACE': imgui.KEY_SPACE,
            'RET': imgui.KEY_ENTER,
            'ESC': imgui.KEY_ESCAPE,
            'PAGE_UP': imgui.KEY_PAGE_UP,
            'PAGE_DOWN': imgui.KEY_PAGE_DOWN,
            'A': imgui.KEY_A,
            'C': imgui.KEY_C,
            'V': imgui.KEY_V,
            'X': imgui.KEY_X,
            'Y': imgui.KEY_Y,
            'Z': imgui.KEY_Z,
            'LEFT_CTRL': imgui.KEY_MOD_CTRL,
            'RIGHT_CTRL': imgui.KEY_MOD_CTRL,
            'LEFT_ALT': imgui.KEY_MOD_ALT,
            'RIGHT_ALT': imgui.KEY_MOD_ALT,
            'LEFT_SHIFT': imgui.KEY_MOD_SHIFT,
            'RIGHT_SHIFT': imgui.KEY_MOD_SHIFT,
            # 'OSKEY': imgui.OSKEY_OSKEY,
        }

        # 根据事件类型更新 ImGui 的键盘状态
        if event_type in key_map:
            k = key_map[event_type]
            # io.add_key_event(k, is_press)
            io.add_input_character(k)
