from . import preferences, ops, keymap
bl_info = {
    "name": "Color Picker",
    "author": "AIGODLIKE Community, Cupcko <649730016@qq.com>, 小萌新",
    "version": (1, 0, 6),
    "blender": (4, 0, 0),
    "location": "3D View,Image Editor",
    "description": "Simple picker color in Blender",
    "category": "Paint"
}


def register():
    ops.register()
    keymap.register()
    preferences.register()


def unregister():
    keymap.unregister()
    ops.unregister()
    preferences.unregister()
