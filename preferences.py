import bpy
import rna_keymap_ui


class ColorPickerPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    picker_switch: bpy.props.BoolProperty(name="picker switch", description="Switch color picker", default=True)

    def draw(self, context):
        layout = self.layout
        # box = layout.box()
        
        layout.prop(self, "picker_switch")
        try:
            from imgui_bundle import imgui
        except:
            layout.label(text="imgui未安装,请安装")
        else:
            layout.label(text="imgui安装完成")

        # self.draw_keymaps(box)
    def draw_keymaps(self, layout):
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user

        split = layout.split()

        b = split.box()
        b.label(text="Tools")

        # if not self.draw_tool_keymaps(kc, keys, b):pass

    def draw_tool_keymaps(self, kc, keysdict, layout):
        drawn = False

        for name in keysdict:
            if "PIE" not in name:
                keylist = keysdict.get(name)

                if self.draw_keymap_items(kc, name, keylist, layout) and not drawn:
                    drawn = True

        return drawn

    def draw_keymap_items(self,kc, name, keylist, layout):
        drawn = []

        idx = 0

        for item in keylist:
            keymap = item.get("keymap")
            isdrawn = False

            if keymap:
                km = kc.keymaps.get(keymap)

                kmi = None
                if km:
                    idname = item.get("idname")

                    for kmitem in km.keymap_items:
                        if kmitem.idname == idname:
                            properties = item.get("properties")

                            if properties:
                                if all([getattr(kmitem.properties, name, None) == value for name, value in properties]):
                                    kmi = kmitem
                                    break

                            else:
                                kmi = kmitem
                                break

                if kmi:
                    if idx == 0:
                        box = layout.box()

                    if len(keylist) == 1:
                        label = name.title().replace("_", " ")

                    else:
                        if idx == 0:
                            box.label(text=name.title().replace("_", " "))

                        label = item.get("label")

                    row = box.split(factor=0.25)
                    row.label(text=label)

                    rna_keymap_ui.draw_kmi(["ADDON", "USER", "DEFAULT"], kc, km, kmi, row, 0)

                    infos = item.get("info", [])
                    for text in infos:
                        row = box.split(factor=0.20)
                        row.separator()
                        row.label(text=text, icon="INFO")

                    isdrawn = True
                    idx += 1

            drawn.append(isdrawn)

        return any(d for d in drawn)


def register():
    bpy.utils.register_class(ColorPickerPreferences)


def unregister():
    bpy.utils.unregister_class(ColorPickerPreferences)
