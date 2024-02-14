from engine3d.objects.model import SkyBox, Hovercraft, BaseModel, Cube
from typing import List


class Scene:
    def __init__(self, app) -> None:
        self.app = app
        self.objects: List[BaseModel] = list()
        self.load()

    def load(self) -> None:
        self.objects.append(SkyBox(self.app))
        self.objects.append(Hovercraft(self.app,
                                       scale=(0.1, 0.1, 0.1),
                                       rot=(0, 0, 0),
                                       pos=(0, -1, 0)))
        # floor
        n, s = 20, 2
        for x in range(-n, n, s):
            for z in range(-n, n, s):
                self.objects.append(Cube(self.app, pos=(x, -s, z), tex_id='cube'))

    def render(self) -> None:
        [obj.render() for obj in self.objects]
