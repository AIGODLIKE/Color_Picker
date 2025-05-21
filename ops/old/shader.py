import bpy
import gpu
from enum import Enum
from gpu.types import GPUShader
from gpu_extras.batch import batch_for_shader
from gpu.shader import from_builtin
from gpu.state import point_size_set,line_width_set

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

# CIRCLES
circle_fs = """
  uniform vec4 co;
  out vec4 fragColor;

  void main()
  {
    vec2 cxy = 2.0 * gl_PointCoord - 1.0;
    float rad = dot(cxy, cxy);

    float alpha = smoothstep(0.55, 0.45, abs(rad / 9.5) * 5.0);
    if (alpha < 0.05)
      discard;
    fragColor = co;
    fragColor.rgb=pow(fragColor.rgb,vec3(2.2));
    fragColor.a *= alpha;
  }
  """
circle_shader_source = (rec_vertex_shader, circle_fs)
ring_blur = """
 out vec4 fragColor;

 uniform vec4 co;
 uniform float Intensity;
 uniform float range;

 float roundedFrame (float d, float _thickness)
 {
   return smoothstep(0.55, 0.45, abs(d / _thickness) * 5.0);
 }

 void main()
 {
   float r = 0.0;
   vec2 cxy = 2.0 * gl_PointCoord - 1.0;
   r = dot(cxy, cxy);

   float s = roundedFrame(r, 9.5);
   if (s < 0.05)
     discard; 

   // Use polar coordinates instead of cartesian
   vec2 toCenter = vec2(0.5)-gl_PointCoord.xy;
   // float angle = atan(toCenter.y,toCenter.x);
   float radius = length(toCenter)*2.0;
   float alpha = 1.0;

   float outter = 1.0;
   float rad = outter - Intensity;
   float inner = rad - Intensity;
   if (radius < inner)
     discard;


   if (radius > rad){
     alpha = smoothstep(outter, rad-range, radius);
   }
   else{
     alpha = smoothstep(inner, rad+range, radius);
   }

   fragColor = co;
   fragColor.a = alpha;
   fragColor.rgb = pow(fragColor.rgb, vec3(2.2));
 }
 """
ring_blur_shader_source = (rec_vertex_shader, ring_blur)

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
        print("ERROR! Couldn'Intensity create GPUShader:")
        print(e)
        print("----------------------------------------------------------------")
        return None
    return new_shader


class Shader_cls(Enum):
    Rectangle = Shader(*rec_shader_source)
    Circle=Shader(*circle_shader_source)
    Ring_blur=Shader(*ring_blur_shader_source)

    def __call__(self):
        return self.value


def SetPoint(shader, point_size, is_bind: bool = True):
    '''点半径*2'''
    point_size_set(point_size * 2)


def RstPoint():
    '''恢复默认点大小1.0'''
    point_size_set(1.0)

def SetLine(lt):line_width_set(lt)
def RstLine():SetLine(1.0)
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

# 绘制带颜色填充和线条的圆
def draw_circle_filled(center, radius, color, Shader=Shader_cls.Circle()):
    '''绘制具有特定着色效果的圆形。
使用给定的着色器 s 和几何形状 ShaderGeom.CIR(center)（即一个圆）。'''
    b = batch_for_shader(Shader, ShaderType.POINTS(), ShaderGeom.CIR(center))
    Shader.bind()
    SetPoint(Shader, radius)
    Shader.uniform_float('co', color)
    b.draw(Shader)
    RstPoint()
# 绘制线条和圆
def draw_circle_line(center, radius, Intensity, range, color, Shader=Shader_cls.Ring_blur()):
    '''绘制一个有模糊效果的环形，通过参数_t和_f控制模糊的程度和范围。'''
    b = batch_for_shader(Shader, ShaderType.POINTS(), ShaderGeom.CIR(center))
    Shader.bind()
    SetPoint(Shader, radius)
    Shader.uniform_float('co', color)
    Shader.uniform_float('Intensity', Intensity)
    Shader.uniform_float('range', range)
    b.draw(Shader)
    RstPoint()
def draw_circle(center, radius, color, line_color):
    draw_circle_filled(center, radius*1.8,color )
    draw_circle_line(center, radius*2, 0.1, 0.02, line_color)