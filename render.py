from .extern.imgui_bundle.python_backends.base_backend import BaseOpenGLRenderer
from .extern.imgui_bundle import imgui
import gpu
import bpy
import ctypes
import platform
import time
from gpu_extras.batch import batch_for_shader
from gpu.types import GPUShader, GPUBatch, GPUVertBuf, GPUIndexBuf
import numpy as np


class Renderer(BaseOpenGLRenderer):
    vertex_source="""
                in  vec3 Position;
                in  vec2 UV;
                in  vec4 Color;
                out vec2 Frag_UV;
                out vec4 final_col;
                uniform mat4 ProjMtx;
                
                void main() {
                    Frag_UV = UV;
                    final_col=Color;
                    final_col.rgb = pow(final_col.rgb,vec3(2.2));
                    final_col.rgb*=vec3(final_col.a);
                    final_col.a=1.0-pow(1.0-final_col.a,2.2);
                    gl_Position = ProjMtx * vec4(Position.xy, 0, 1);
                }
                """
    fragment_source="""
                    in vec2 Frag_UV;
                    in vec4 final_col;
                    out vec4 Frag_Color;
                    uniform sampler2D Texture;
                    vec4 linear_to_srgb(vec4 linear) {
                        return mix(
                            1.055 * pow(linear, vec4(1.0 / 2.4)) - 0.055,
                            12.92 * linear,
                            step(linear, vec4(0.0031308))
                        );
                    }

                    vec4 srgb_to_linear(vec4 srgb) {
                        return mix(
                            pow((srgb + 0.055) / 1.055, vec4(2.4)),
                            srgb / 12.92,
                            step(srgb, vec4(0.04045))
                        );
                    }

                    void main() {
                        
                        Frag_Color = final_col; // 输出sRGB颜色
                        Frag_Color  = (texture(Texture, Frag_UV.st)) *Frag_Color;
                        Frag_Color.rgb = pow(Frag_Color.rgb,vec3(2.2)); // 输出sRGB颜色
                        Frag_Color.a = pow(Frag_Color.a,2.2); // 输出sRGB颜色
                    }
                                                """
    instance = None

    def __init__(self):
        self._shader_handle = None
        self._vert_handle = None
        self._fragment_handle = None

        self._attrib_location_tex = None
        self._attrib_proj_mtx = None
        self._attrib_location_position = None
        self._attrib_location_uv = None
        self._attrib_location_color = None

        self._vbo_handle = None
        self._elements_handle = None
        self._vao_handle = None
        self._font_tex = None
        Renderer.instance = self

        super(Renderer,self).__init__()

    def refresh_font_texture(self):
        self.refresh_font_texture_ex(self)
        if self.refresh_font_texture_ex not in bpy.app.handlers.load_post:
            bpy.app.handlers.load_post.append(self.refresh_font_texture_ex)

    @staticmethod
    @bpy.app.handlers.persistent
    def refresh_font_texture_ex(scene=None):
        # save texture state
        # print('refresh_font_texture_ex')
        self = Renderer.instance
        if not (img := bpy.data.images.get(".imgui_font", None)) \
                or (platform.platform == "win32" and img.bindcode == 0):
            ts = time.time()
            # width, height, pixels,a = self.io.fonts.get_tex_data_as_rgba32()
            font_matrix: np.ndarray = self.io.fonts.get_tex_data_as_rgba32()
            width = font_matrix.shape[1]
            height = font_matrix.shape[0]
            pixels = font_matrix.data
            if not img:
                img = bpy.data.images.new(".imgui_font", width, height, alpha=True, float_buffer=True)

                # img.colorspace_settings.name = 'Non-Color'
            pixels = np.frombuffer(pixels, dtype=np.uint8) / np.float32(256)
            # 进行伽马校正（假设伽马值为 2.2）
            # gamma = 2.2
            # pixels = np.power(pixels, 1.0 / gamma)
            img.pixels.foreach_set(pixels)

            self.io.fonts.clear_tex_data()
            # print('update font texture')
            # logger.debug(f"MLT Init -> {time.time() - ts:.2f}s")
        img.gl_load()
        self._font_tex = gpu.texture.from_image(img)
        self._font_texture = img.bindcode
        bpy.data.images.remove(img)
        # self.io.fonts.tex_id = self._font_texture


    def _create_device_objects(self):
        shader = gpu.types.GPUShader(self.vertex_source, self.fragment_source, )


        self._bl_shader = shader
        # se
    def _invalidate_device_objects(self):
        if self._font_texture is not None and self._font_texture != 0:
            self._font_texture.free()  # 使用 gpu 模块的 free 方法释放纹理资源
        self.io.fonts.texture_id = 0
        self._font_texture = 0

        # def _invalidate_device_objects(self):
        #     if self._font_texture > -1:
        #         gl.glDeleteTextures([self._font_texture])
        #     self.io.fonts.texture_id = 0
        #     self._font_texture = 0

    def render(self, draw_data):
        io = self.io
        shader = self._bl_shader

        # 获取显示尺寸和缩放后的帧缓冲区尺寸
        display_width, display_height = io.display_size
        fb_width = int(display_width * io.display_framebuffer_scale[0])
        fb_height = int(display_height * io.display_framebuffer_scale[1])

        # 如果帧缓冲区宽度或高度为0，则退出函数
        if fb_width == 0 or fb_height == 0:
            return

        # 根据显示缩放比例调整剪裁矩形
        draw_data.scale_clip_rects(io.display_framebuffer_scale)

        #记录上一帧
        last_enable_blend = gpu.state.blend_get()
        last_enable_depth_test = gpu.state.depth_test_get()
        # 设置图形管线的状态
        gpu.state.blend_set('ALPHA')  # 设置混合模式为透明
        gpu.state.depth_test_set('LESS_EQUAL')  # 禁用深度测试
        # gpu.state.face_culling_set('NONE')  # 禁用面剔除
        gpu.state.program_point_size_set(False)  # 不使用程序设置的点大小
        gpu.state.scissor_test_set(True)  # 启用剪裁测试
        # self.refresh_font_texture_ex()
        # 绑定着色器并设置投影矩阵
        shader.bind()
        shader.uniform_float("ProjMtx", self._create_projection_matrix(display_width, display_height))
        shader.uniform_sampler("Texture", self._font_tex)  # 设置纹理采样器

        # 遍历所有的绘制命令列表
        for commands in draw_data.cmd_lists:
            # 获取索引缓冲区的大小和地址，转换为numpy数组
            # size = commands.idx_buffer_size * imgui.INDEX_SIZE // 4
            size = commands.idx_buffer.size()* imgui.INDEX_SIZE // 4
            # address = commands.idx_buffer_data
            address = commands.idx_buffer.data_address()
            idx_buffer_np = np.ctypeslib.as_array(ctypes.cast(address, ctypes.POINTER(ctypes.c_int)), shape=(size,))

            # 获取顶点缓冲区的大小和地址，转换为numpy数组
            # size = commands.vtx_buffer_size * imgui.VERTEX_SIZE // 4
            size = commands.vtx_buffer.size()* imgui.VERTEX_SIZE // 4
            # address = commands.vtx_buffer_data
            address = commands.vtx_buffer.data_address()
            vtx_buffer_np = np.ctypeslib.as_array(ctypes.cast(address, ctypes.POINTER(ctypes.c_float)), shape=(size,))
            vtx_buffer_shaped = vtx_buffer_np.reshape(-1, imgui.VERTEX_SIZE // 4)

            idx_buffer_offset = 0
            # 遍历每个绘制命令
            for command in commands.cmd_buffer:
                # 设置剪裁矩形
                x, y, z, w = command.clip_rect
                gpu.state.scissor_set(int(x), int(fb_height - w), int(z - x), int(w - y))

                # 提取顶点、UV和颜色信息，准备绘制
                vertices = vtx_buffer_shaped[:, :2]
                uvs = vtx_buffer_shaped[:, 2:4]
                colors = vtx_buffer_shaped.view(np.uint8)[:, 4 * 4:].astype('f') / 255.0

                # 提取索引数据
                indices = idx_buffer_np[idx_buffer_offset:idx_buffer_offset + command.elem_count]

                # 创建批处理对象并绘制
                batch = batch_for_shader(shader, 'TRIS', {
                    "Position": vertices,
                    "UV": uvs,
                    "Color": colors,
                }, indices=indices)
                batch.draw(shader)

                # 更新索引缓冲区偏移
                idx_buffer_offset += command.elem_count
        # if last_enable_blend:
        #     gpu.state.blend_set(last_enable_blend)
        # else:
        gpu.state.blend_set('NONE')
        # if last_enable_depth_test:
        #     gpu.state.depth_test_set(last_enable_depth_test)
        # else:
        #     gpu.state.depth_test_set('NONE')
        gpu.state.scissor_test_set(False)  # 启用剪裁测试
    #     # Restore previous GPU state
    #     # gpu.state.active_set(state)

    def _create_projection_matrix(self, width, height):
        ortho_projection = (
            2.0 / width, 0.0, 0.0, 0.0,
            0.0, 2.0 / -height, 0.0, 0.0,
            0.0, 0.0, -1.0, 0.0,
            -1.0, 1.0, 0.0, 1.0
        )
        return ortho_projection
