from engine.objects.vbo import VBO_List, BaseVBO
from engine.shaders.shader_program import ShaderProgram
import moderngl as mgl


class VAO:
    def __init__(self, ctx: mgl.Context) -> None:
        self.ctx: mgl.Context = ctx
        self.vbo: VBO_List = VBO_List(ctx)
        self.program = ShaderProgram(ctx)
        self.vaos = dict()

        self.vaos['skybox'] = self.get_vao(
            program=self.program.programs['skybox'],
            vbo=self.vbo.vbos['skybox'])

        # self.vaos['hovercraft'] = self.get_vao(
         #   program=self.program.programs['default'],
         #   vbo=self.vbo.vbos['hovercraft'])

    def get_vao(self, program: mgl.Program, vbo: BaseVBO) -> mgl.VertexArray:
        return self.ctx.vertex_array(program,
                                     [(vbo.vbo, vbo.format, *vbo.attribs)],
                                     skip_errors=True)

    def release(self):
        self.vbo.release()
        self.program.release()
