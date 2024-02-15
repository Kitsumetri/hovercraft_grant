import moderngl as mgl

from engine3d.objects.vbo import VBO_List, BaseVBO
from engine3d.shaders.shader_program import ShaderProgram
from typing import Dict


class VAO:
    def __init__(self, ctx: mgl.Context) -> None:
        self.ctx: mgl.Context = ctx
        self.vbo: VBO_List = VBO_List(ctx)
        self.program: ShaderProgram = ShaderProgram(ctx)
        self.vaos: Dict[str, mgl.VertexArray] = dict()

        self.on_init()

    def on_init(self) -> None:
        self.vaos.update(
            {'hovercraft': self.get_vao(self.program.programs['default'], self.vbo.vbos['hovercraft'])}
        )

        self.vaos.update(
            {'cube': self.get_vao(self.program.programs['default'], self.vbo.vbos['cube'])}
        )

        self.vaos.update(
            {'skybox': self.get_vao(self.program.programs['skybox'], self.vbo.vbos['skybox'])}
        )

    def get_vao(self, program: mgl.Program, vbo: BaseVBO) -> mgl.VertexArray:
        return self.ctx.vertex_array(program,
                                     [(vbo.vbo, vbo.format, *vbo.attribs)],
                                     skip_errors=True)

    def release(self) -> None:
        self.vbo.release()
        self.program.release()
