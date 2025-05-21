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


from .zh_CN import zh_CN

Colorpickerzh_CN = TranslationHelper('Colorpickerzh_CN', zh_CN.data)
Colorpickerzh_HANS = TranslationHelper('Colorpickerzh_HANS', zh_CN.data, lang='zh_HANS')


def register():
    if bpy.app.version < (4, 0, 0):
        Colorpickerzh_CN.register()
    else:
        Colorpickerzh_CN.register()
        Colorpickerzh_HANS.register()


def unregister():
    if bpy.app.version < (4, 0, 0):
        Colorpickerzh_CN.unregister()
    else:
        Colorpickerzh_CN.unregister()
        Colorpickerzh_HANS.unregister()
