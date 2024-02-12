from typing import List, Tuple, Dict
import moderngl as mgl
import numpy as np
from pywavefront import Wavefront

class BaseVBO:
    def __init__(self, ctx: mgl.Context) -> None:
        self.ctx: mgl.Context = ctx
        self.vbo: mgl.Buffer = self.get_vbo()
        self.format: str | None = None
        self.attribs: list | None = None

    def get_vertex_data(self) -> np.array:
        pass

    def get_vbo(self) -> mgl.Buffer:
        return self.ctx.buffer(self.get_vertex_data())

    def release(self) -> None:
        self.vbo.release()


class SkyBoxVBO(BaseVBO):
    def __init__(self, ctx: mgl.Context) -> None:
        super().__init__(ctx)
        self.format: str = '3f'
        self.attribs: List[str] = ['in_position']

    @staticmethod
    def get_data(vertices: List[Tuple[int, int, int]], indices: List[Tuple[int, int, int]]) -> np.array:
        data: List[Tuple[int, int, int]] = [vertices[ind] for triangle in indices for ind in triangle]
        return np.array(data, dtype='f4')

    def get_vertex_data(self) -> np.array:
        vertices: List[Tuple[int, int, int]] = \
            [(-1, -1, 1), (1, -1, 1),
             (1, 1, 1), (-1, 1, 1),
             (-1, 1, -1), (-1, -1, -1),
             (1, -1, -1), (1, 1, -1)
             ]

        indices: List[Tuple[int, int, int]] = \
            [(0, 2, 3), (0, 1, 2),
             (1, 7, 2), (1, 6, 7),
             (6, 5, 4), (4, 7, 6),
             (3, 4, 5), (3, 5, 0),
             (3, 7, 4), (3, 2, 7),
             (0, 6, 1), (0, 5, 6)
             ]

        vertex_data: np.array = self.get_data(vertices, indices)
        vertex_data: np.array = np.flip(vertex_data, 1).copy(order='C')
        return vertex_data


class HovercraftVBO(BaseVBO):
    def __init__(self, app) -> None:
        super().__init__(app)
        self.format: str = '2f 3f 3f'
        self.attribs: List[str] = ['in_texcoord_0', 'in_normal', 'in_position']

    def get_vertex_data(self) -> np.array:
        objs: Wavefront = Wavefront('engine/graphics/assets/obj/Hovecraft2/1.obj',
                                    create_materials=True, cache=True, parse=True)
        vertices: List[np.array] = list()
        for obj in objs.materials.values():
            vertices.extend(obj.vertices)
        return np.array(vertices, dtype='f4')


class VBO_List:
    def __init__(self, ctx: mgl.Context) -> None:
        self.vbos: Dict[str, BaseVBO] = dict()
        self.vbos.update({'skybox': SkyBoxVBO(ctx)})
        self.vbos.update({'hovercraft': HovercraftVBO(ctx)})

    def release(self) -> None:
        [vbo.release() for vbo in self.vbos.values()]
