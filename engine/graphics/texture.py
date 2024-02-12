import pygame as pg
import moderngl as mgl
from typing import List, Tuple, Dict


class Texture:
    def __init__(self, app):
        self.app = app
        self.ctx: mgl.Context = app.ctx
        self.textures: Dict[str, mgl.TextureCube] = dict()
        self.textures['skybox'] = self.get_texture_cube(dir_path='engine/graphics/textures/skybox/',
                                                        ext='png')

    def get_texture_cube(self, dir_path: str, ext: str = 'png') -> mgl.TextureCube:
        faces: List[str] = ['right', 'left', 'top', 'bottom'] + ['front', 'back'][::-1]
        textures: List[pg.Surface] = list()

        for face in faces:
            if face in ['right', 'left', 'front', 'back']:
                texture: pg.Surface = pg.transform.flip(pg.image.load(dir_path + f'{face}.{ext}').convert(),
                                                        flip_x=True, flip_y=False)
            else:
                texture: pg.Surface = pg.transform.flip(pg.image.load(dir_path + f'{face}.{ext}').convert(),
                                                        flip_x=False, flip_y=True)
            textures.append(texture)

        size: Tuple[int, int] = textures[0].get_size()
        texture_cube: mgl.TextureCube = self.ctx.texture_cube(size=size, components=3, data=None)

        for i in range(6):
            texture_data: bytes = pg.image.tostring(textures[i], 'RGB')
            texture_cube.write(face=i, data=texture_data)

        return texture_cube

    def release(self) -> None:
        [tex.release() for tex in self.textures.values()]
