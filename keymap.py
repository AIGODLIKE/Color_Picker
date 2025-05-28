import bpy

keys = [
    {'label': 'Image Paint', 'keymap': 'Image Paint', 'space_type': 'EMPTY',
     'idname': 'paint.color_picker', 'type': 'E', 'value': 'PRESS',
     },
    {'label': '3D Paint Mode', 'keymap': 'Grease Pencil', 'idname': 'paint.color_picker', 'type': 'SPACE',
     'value': 'PRESS', },
]


def get_kmi_operator_properties(kmi: 'bpy.types.KeyMapItem') -> dict:
    """获取kmi操作符的属性
    """
    properties = kmi.properties
    prop_keys = dict(properties.items()).keys()
    dictionary = {i: getattr(properties, i, None) for i in prop_keys}
    del_key = []
    for item in dictionary:
        prop = getattr(properties, item, None)
        typ = type(prop)
        if prop:
            if typ == Vector:
                # 属性阵列-浮点数组
                dictionary[item] = dictionary[item].to_tuple()
            elif typ == Euler:
                dictionary[item] = dictionary[item][:]
            elif typ == Matrix:
                dictionary[item] = tuple(i[:] for i in dictionary[item])
            elif typ == bpy.types.bpy_prop_array:
                dictionary[item] = dictionary[item][:]
            elif typ in (str, bool, float, int, set, list, tuple):
                ...
            elif typ.__name__ in [
                'TRANSFORM_OT_shrink_fatten',
                'TRANSFORM_OT_translate',
                'TRANSFORM_OT_edge_slide',
                'NLA_OT_duplicate',
                'ACTION_OT_duplicate',
                'GRAPH_OT_duplicate',
                'TRANSFORM_OT_translate',
                'OBJECT_OT_duplicate',
                'MESH_OT_loopcut',
                'MESH_OT_rip_edge',
                'MESH_OT_rip',
                'MESH_OT_duplicate',
                'MESH_OT_offset_edge_loops',
                'MESH_OT_extrude_faces_indiv',
            ]:  # 一些奇怪的操作符属性,不太好解析也用不上
                ...
                del_key.append(item)
            else:
                print('emm 未知属性,', typ, dictionary[item])
                del_key.append(item)
    for i in del_key:
        dictionary.pop(i)
    return dictionary


def draw_keymap(layout):
    from rna_keymap_ui import draw_kmi

    kc = bpy.context.window_manager.keyconfigs.user
    for km, kmi in keymaps:
        km = kc.keymaps.get(km.name)
        if km:
            kmi = km.keymap_items.get(kmi.idname, get_kmi_operator_properties(kmi))
            if kmi:
                layout.label(text=km.name)
                draw_kmi(["USER", "ADDON", "DEFAULT"], kc, km, kmi, layout, 0)


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


keymaps = []

def register():
    global keymaps
    keymaps = register_keymaps(keys)


def unregister():
    global keymaps
    if keymaps:
        unregister_keymaps(keymaps)
