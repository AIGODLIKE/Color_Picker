from . import preferences
bl_info = {
    "name": "Color Picker",
    "author": "AIGODLIKE Community, Cupcko <649730016@qq.com>, 小萌新",
    "version": (1, 0, 4),
    "blender": (4, 0, 0),
    "location": "3D View,Image Editor",
    "description": "Simple picker color in Blender",
    "category": "Paint"
}


def register():
    preferences.register()


def unregister():
    preferences.unregister()
