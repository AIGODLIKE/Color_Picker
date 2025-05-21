import bpy

keys = {
    'COLOR_PICKER': [
        {'label': 'Texture Paint Mode', 'keymap': 'Image Paint', 'space_type': 'VIEW_3D',
         'idname': 'paint.color_picker',
         'type': 'SPACE', 'value': 'PRESS', },
        {'label': 'Vertex Paint Mode', 'keymap': 'Vertex Paint', 'space_type': 'VIEW_3D',
         'idname': 'paint.color_picker', 'type': 'SPACE', 'value': 'PRESS',
         },
        {'label': 'UV Paint Mode', 'keymap': 'Image Generic', 'space_type': 'IMAGE_EDITOR',
         'idname': 'paint.color_picker', 'type': 'Z',
         'value': 'PRESS', },
        {'label': 'Sculpt Paint Mode', 'keymap': 'Sculpt', 'idname': 'paint.color_picker', 'type': 'SPACE',
         'value': 'PRESS', },
        {'label': '3D Paint Mode', 'keymap': 'Grease Pencil', 'idname': 'paint.color_picker', 'type': 'SPACE',
         'value': 'PRESS', },
        {'label': 'Window', 'keymap': 'Window', 'idname': 'paint.color_picker', 'type': 'SPACE',
         'value': 'PRESS', },
    ],
}


def register_keymaps(keylist):
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    keymaps = []

    if kc:

        for item in keylist:
            keymap = item.get("keymap")
            space_type = item.get("space_type", "EMPTY")

            if keymap:
                km = kc.keymaps.new(name=keymap, space_type=space_type)

                if km:
                    idname = item.get("idname")
                    type = item.get("type")
                    value = item.get("value")

                    shift = item.get("shift", False)
                    ctrl = item.get("ctrl", False)
                    alt = item.get("alt", False)

                    kmi = km.keymap_items.new(idname, type, value, shift=shift, ctrl=ctrl, alt=alt)

                    if kmi:
                        properties = item.get("properties")

                        if properties:
                            for name, value in properties:
                                setattr(kmi.properties, name, value)

                        active = item.get("active", True)
                        kmi.active = active

                        keymaps.append((km, kmi))
    else:
        print("WARNING: Keyconfig not availabe, skipping color picker keymaps")

    return keymaps


def unregister_keymaps(keymaps):
    for km, kmi in keymaps:
        km.keymap_items.remove(kmi)


keymaps = None


def register():
    global keymaps
    keymaps = register_keymaps(keys['COLOR_PICKER'])


def unregister():
    global keymaps
    if keymaps:
        unregister_keymaps(keymaps)
