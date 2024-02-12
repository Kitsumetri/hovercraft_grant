import moderngl as mgl
from typing import Dict


class ShaderProgram:
    def __init__(self, ctx) -> None:
        self.ctx: mgl.Context = ctx
        self.programs: Dict[str, mgl.Program] = dict()

        self.programs.update({'default': self.get_program('default')})
        self.programs.update({'skybox': self.get_program('skybox')})

    def get_program(self, shader_name: str) -> mgl.Program:
        with open(f"engine/shaders/verts/{shader_name}.vert") as vert_file:
            vertex_shader = vert_file.read()

        with open(f"engine/shaders/frags/{shader_name}.frag") as frag_file:
            fragment_shader = frag_file.read()

        program = self.ctx.program(vertex_shader=vertex_shader,
                                   fragment_shader=fragment_shader)
        return program

    def release(self):
        [program.release() for program in self.programs.values()]
