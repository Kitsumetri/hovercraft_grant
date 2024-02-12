from engine.objects.model import SkyBox, Hovercraft, BaseModel
from typing import List


class Scene:
    def __init__(self, app) -> None:
        self.app = app
        self.objects: List[BaseModel] = list()
        self.load()

    def load(self):
        self.objects.append(SkyBox(self.app))
        self.objects.append(Hovercraft(self.app, scale=(0.001, 0.001, 0.001)))

    def render(self):
        [obj.render() for obj in self.objects]
