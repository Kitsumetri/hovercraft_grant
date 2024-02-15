import moderngl as mgl
from typing import Dict


class ShaderProgram:
    def __init__(self, ctx) -> None:
        self.ctx: mgl.Context = ctx
        self.programs: Dict[str, mgl.Program] = dict()

        self.programs.update({'default': self.get_program('default')})
        self.programs.update({'skybox': self.get_program('skybox')})

    def get_program(self, shader_name: str) -> mgl.Program:
        with open(f"engine3d/shaders/verts/{shader_name}.vert") as vert_file:
            vertex_shader: str = vert_file.read()

        with open(f"engine3d/shaders/frags/{shader_name}.frag") as frag_file:
            fragment_shader: str = frag_file.read()

        program: mgl.Program = self.ctx.program(vertex_shader=vertex_shader,
                                                fragment_shader=fragment_shader)
        return program

    def release(self) -> None:
        [program.release() for program in self.programs.values()]
