import bpy


class SyncKey:

    def sync_key(self, context: bpy.types.Context, event: bpy.types.Event):
        import imgui
        io = imgui.get_io()

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
            'LEFT_CTRL': 128 + 1,
            'RIGHT_CTRL': 128 + 2,
            'LEFT_ALT': 128 + 3,
            'RIGHT_ALT': 128 + 4,
            'LEFT_SHIFT': 128 + 5,
            'RIGHT_SHIFT': 128 + 6,
            'OSKEY': 128 + 7,
        }

        if event.type in key_map:
            if event.value == 'PRESS':
                io.keys_down[key_map[event.type]] = True
            elif event.value == 'RELEASE':
                io.keys_down[key_map[event.type]] = False

        io.key_ctrl = (
                io.keys_down[key_map['LEFT_CTRL']] or
                io.keys_down[key_map['RIGHT_CTRL']]
        )

        io.key_alt = (
                io.keys_down[key_map['LEFT_ALT']] or
                io.keys_down[key_map['RIGHT_ALT']]
        )

        io.key_shift = (
                io.keys_down[key_map['LEFT_SHIFT']] or
                io.keys_down[key_map['RIGHT_SHIFT']]
        )

        io.key_super = io.keys_down[key_map['OSKEY']]

        io.mouse_pos = (self.mouse[0], context.region.height - 1 - self.mouse[1])
        if event.type == 'LEFTMOUSE':
            io.mouse_down[0] = event.value == 'PRESS'
        # if not self.candicates_words:
        if event.type == 'WHEELUPMOUSE':
            io.mouse_wheel = +1
        elif event.type == 'WHEELDOWNMOUSE':
            io.mouse_wheel = -1

        if event.unicode and 0 < (char := ord(event.unicode)) < 0x10000:
            io.add_input_character(char)

    def setup_key_map(self):
        import imgui
        io = imgui.get_io()
        keys = (
            imgui.KEY_TAB,
            imgui.KEY_LEFT_ARROW,
            imgui.KEY_RIGHT_ARROW,
            imgui.KEY_UP_ARROW,
            imgui.KEY_DOWN_ARROW,
            imgui.KEY_HOME,
            imgui.KEY_END,
            imgui.KEY_INSERT,
            imgui.KEY_DELETE,
            imgui.KEY_BACKSPACE,
            imgui.KEY_ENTER,
            imgui.KEY_ESCAPE,
            imgui.KEY_PAGE_UP,
            imgui.KEY_PAGE_DOWN,
            imgui.KEY_A,
            imgui.KEY_C,
            imgui.KEY_V,
            imgui.KEY_X,
            imgui.KEY_Y,
            imgui.KEY_Z,
        )
        for k in keys:
            # We don't directly bind Blender's event type identifiers
            # because imgui requires the key_map to contain integers only
            io.key_map[k] = k
