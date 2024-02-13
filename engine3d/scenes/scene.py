from engine3d.objects.model import SkyBox, Hovercraft, BaseModel
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

    def render(self) -> None:
        [obj.render() for obj in self.objects]
