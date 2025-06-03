import bpy

def sync_key(self, context: bpy.types.Context, event: bpy.types.Event):
    from imgui_bundle import imgui
    io = imgui.get_io()

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
