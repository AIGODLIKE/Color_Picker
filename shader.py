import bpy
import gpu
from gpu_extras.batch import batch_for_shader

c_vertex_shader = """
// 顶点着色器
uniform mat4 ModelViewProjectionMatrix;

in vec2 pos;
in vec3 color; // 添加颜色输入
out vec3 v_color; // 输出到片段着色器的颜色

void main() {
    gl_Position = ModelViewProjectionMatrix * vec4(pos, 1.0, 1.0);
    v_color = color; // 直接传递颜色
}
"""

c_fragment_shader = """
// 片段着色器
in vec3 v_color;
out vec4 fragColor;

void main() {
    fragColor = vec4(v_color, 1.0);
}
"""


def draw_callback(vertices):
    # vertices = [(10.0, 10.0), (20.0, 200.0), (30.0, 30.0)]
    colors = [(1.0, 1.0, 1.0), (0.0, 0.0, 0.0), (0.0, 1.0, 0.0)]  # 对应的颜色值
    shader = gpu.types.GPUShader(c_vertex_shader, c_fragment_shader)
    batch = batch_for_shader(shader, 'TRIS', {"pos": vertices, "color": colors})

    shader.bind()
    # shader.uniform_float("ModelViewProjectionMatrix", bpy.context.region_data.perspective_matrix)
    batch.draw(shader)


class DrawColorTriangleOperator(bpy.types.Operator):
    bl_idname = "view3d.draw_color_triangle_operator"
    bl_label = "Draw Color Triangle"

    def modal(self, context, event):
        if event.type == 'ESC':
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback, args, 'WINDOW', 'POST_PIXEL')
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}


def menu_func(self, context):
    self.layout.operator(DrawColorTriangleOperator.bl_idname)


def register():
    bpy.utils.register_class(DrawColorTriangleOperator)
    bpy.types.VIEW3D_MT_view.append(menu_func)


def unregister():
    bpy.utils.unregister_class(DrawColorTriangleOperator)
    bpy.types.VIEW3D_MT_view.remove(menu_func)


if __name__ == "__main__":
    register()

from enum import Enum
from gpu.types import GPUShader
from gpu_extras.batch import batch_for_shader
from gpu.shader import from_builtin
from gpu.state import point_size_set

rec_vertex_shader = """
uniform mat4 ModelViewProjectionMatrix;
uniform float size;

in vec2 p;

void main()
{
  gl_Position = ModelViewProjectionMatrix * vec4(p, 1.0, 1.0);
  gl_PointSize = size;
}
"""
rec_fragment_shader = """
// 定义一个常量PI_4，表示π/4的值
float PI_4 = 0.785398;
uniform float h;
out vec4 fragColor;

// 定义一个函数，将HSV颜色值转换为RGB颜色值
vec3 hsv2rgb(vec3 c)
{
    // 定义一个向量K，用于辅助HSV到RGB的转换
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    // 计算彩色环的三个部分，以生成彩色环的效果
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    // 根据HSV模型，通过混合和限制操作，计算RGB颜色
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

// 主函数，由GPU在渲染每个片段时调用
void main()
{
    // 计算饱和度S，线性插值由片段的水平坐标决定
    float S = mix(0, 1, gl_PointCoord.x);
    // 计算明度V，线性插值由片段的垂直坐标决定
    float V = mix(1, 0, gl_PointCoord.y);
    // 使用HSV到RGB的转换函数，并进行伽马校正
    fragColor.rgb = pow(hsv2rgb(vec3(h, S, V)), vec3(2.2));
    //fragColor.rgb = hsv2rgb(vec3(h, S, V));
    // 设置alpha值为1，完全不透明
    fragColor.a = 1.0;
}

  """
rec_shader_source = (rec_vertex_shader, rec_fragment_shader)
tri_vertex_shader = """
uniform mat4 ModelViewProjectionMatrix;
in vec2 pos;
in vec3 color;
out vec3 v_color;

void main()
{
    gl_Position = ModelViewProjectionMatrix * vec4(pos, 0.0, 1.0);
    v_color = color; // 直接传递颜色
}
"""

tri_fragment_shader = """
uniform float h;
in vec3 v_color;
out vec4 fragColor;
vec3 hsv2rgb(vec3 c)
{
    // 定义一个向量K，用于辅助HSV到RGB的转换
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    // 计算彩色环的三个部分，以生成彩色环的效果
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    // 根据HSV模型，通过混合和限制操作，计算RGB颜色
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}
void main()
{
    fragColor = vec4(pow(hsv2rgb(vec3(h,v_color.y,v_color.z)), vec3(2.2)),1.0);
}
"""
tri_shader_source = (tri_vertex_shader, tri_fragment_shader)


class ShaderName2D(Enum):
    IMAGE = 'IMAGE'
    UNIFORM = 'UNIFORM_COLOR'
    FLAT = 'FLAT_COLOR'
    SMOOTH = 'SMOOTH_COLOR'

    def __call__(self):
        return self.value


shader_2d_image = from_builtin(ShaderName2D.IMAGE())
shader_2d_color_unif = from_builtin(ShaderName2D.UNIFORM())
shader_2d_color_flat = from_builtin(ShaderName2D.FLAT())
shader_2d_color_smooth = from_builtin(ShaderName2D.SMOOTH())


class Shader2D(Enum):
    IMAGE = shader_2d_image
    UNIFORM = shader_2d_color_unif
    FLAT = shader_2d_color_flat
    SMOOTH = shader_2d_color_smooth

    def __call__(self):
        return self.value


class ShaderName3D(Enum):
    UNIFORM = 'UNIFORM_COLOR'
    FLAT = 'FLAT_COLOR'
    SMOOTH = 'SMOOTH_COLOR'

    def __call__(self):
        return self.value


shader_3d_color_unif = from_builtin(ShaderName3D.UNIFORM())
shader_3d_color_flat = from_builtin(ShaderName3D.FLAT())
shader_3d_color_smooth = from_builtin(ShaderName3D.SMOOTH())


class Shader3D(Enum):
    UNIFORM = shader_3d_color_unif
    FLAT = shader_3d_color_flat
    SMOOTH = shader_3d_color_smooth

    def __call__(self):
        return self.value


class BuiltinShaderName(Enum):
    IMAGE = 'IMAGE'
    UNIFORM = 'UNIFORM_COLOR'
    FLAT = 'FLAT_COLOR'
    SMOOTH = 'SMOOTH_COLOR'

    def __call__(self):
        return self.value


builtin_shader_image = from_builtin(BuiltinShaderName.IMAGE())
builtin_shader_color_unif = from_builtin(BuiltinShaderName.UNIFORM())
builtin_shader_color_flat = from_builtin(BuiltinShaderName.FLAT())
builtin_shader_color_smooth = from_builtin(BuiltinShaderName.SMOOTH())


class BuiltinShader(Enum):
    IMAGE = builtin_shader_image
    UNIFORM = builtin_shader_color_unif
    FLAT = builtin_shader_color_flat
    SMOOTH = builtin_shader_color_smooth

    def __call__(self):
        return self.value


class Shader2D(Enum):
    IMAGE = shader_2d_image
    UNIFORM = shader_2d_color_unif
    FLAT = shader_2d_color_flat
    SMOOTH = shader_2d_color_smooth

    def __call__(self):
        return self.value


class ShaderType(Enum):
    '''返回对应渲染形状
    POINTS
    LINES
    TRIS
    LINES_ADJ
    TRIFAN '''
    POINTS = "POINTS"
    LINES = "LINES"
    TRIS = "TRIS"
    LINES_ADJ = "LINES_ADJ"
    TRIFAN = "TRI_FAN"

    def __call__(self):
        return self.value


def get_img_geom(*args):
    '''接收任意数量的参数，用来生成图像的几何数据
        返回一个字典，包含两个键："p" 和 "texco"。
        "p" 键调用 get_img_verts 函数生成顶点坐标，
        "texco" 键调用 get_tex_coord 函数生成纹理坐标。'''
    return {"p": get_img_verts(*args), "texco": get_tex_coord()}


def get_tex_coord():
    '''返回一个固定的纹理坐标集合
    标准化的矩形纹理映射'''
    return ((0, 1), (0, 0), (1, 0), (1, 1))


def get_img_verts(*args):
    ''' args[0] 应该是一个包含 x 和 y 坐标的元组，
        args[1] 是一个包含宽度 w 和高度 h 的元组
        计算并返回一个包含矩形四个角的坐标列表'''
    x, y = args[0]
    w, h = args[1]
    return [
        [x, y + h],
        [x, y],
        [x + w, y],
        [x + w, y + h]
    ]


def get_cir_geom(p):
    '''接收一个参数 p，返回一个包含单个点的字典'''
    return {"p": [p]}


class ShaderGeom(Enum):
    IMG = get_img_geom
    IMG_V = get_img_verts
    IMG_TC = get_tex_coord  # Ref: https://docs.blender.org/api/blender2.8/gpu.html#d-image
    CIR = get_cir_geom  # https://docs.blender.org/api/blender2.8/gpu.html#d-rectangle

    def __call__(self, *args):
        return self.value(*args[0])


def Shader(*shaders) -> GPUShader:
    try:
        new_shader = GPUShader(*shaders)
    except Exception as e:
        print("----------------------------------------------------------------")
        print("ERROR! Couldn't create GPUShader:")
        print(e)
        print("----------------------------------------------------------------")
        return None
    return new_shader


class Shader_cls(Enum):
    Rectangle = Shader(*rec_shader_source)
    Triangle = Shader(*tri_shader_source)

    def __call__(self):
        return self.value


def SetPoint(shader, point_size, is_bind: bool = True):
    '''点半径*2'''
    point_size_set(point_size * 2)


def RstPoint():
    '''恢复默认点大小1.0'''
    point_size_set(1.0)


def draw_rec(center, radius, hue, Shader=Shader_cls.Rectangle()):
    '''
    c 中心
    r 半径
    h 色相浮点数，代表色彩的色相部分
    绘制一个基于色相_h的色彩标记。'''
    batch = batch_for_shader(Shader, ShaderType.POINTS(), ShaderGeom.CIR(center))
    Shader.bind()
    SetPoint(Shader, radius)
    Shader.uniform_float("h", hue)
    batch.draw(Shader)
    RstPoint()


from struct import pack


def draw_tri(vertices, hue, colors, Shader=Shader_cls.Triangle()):
    # draw_callback(vertices)
    # vertices = [(-1.0, 1.0), (-1.0, -1.0), (1.0, 0.0)]
    # colors = [(1.0, 1.0, 1.0), (0.0, 0.0, 0.0), (0.0, 1.0, 0.0)]  # 对应的颜色值
    print('color1',hue)
    shader = gpu.types.GPUShader(tri_vertex_shader, tri_fragment_shader)
    batch = batch_for_shader(shader, 'TRIS', {"pos": vertices, "color": colors})
    shader.uniform_float("h", hue)
    print(bpy.context.tool_settings.vertex_paint.brush.color.h)
    shader.bind()

    # shader.uniform_float("ModelViewProjectionMatrix", bpy.context.region_data.perspective_matrix)
    batch.draw(shader)
