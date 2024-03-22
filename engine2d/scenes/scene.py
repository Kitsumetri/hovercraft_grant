import engine2d.objects.model as e2d_models

from typing import List
from engine2d.objects.model import BaseModel
from pygame.math import Vector2 as vec2


class Scene:
    def __init__(self, app) -> None:
        self.app = app
        self.models: List[BaseModel] = list()
        self.load()

    def load(self) -> None:
        self.models.append(e2d_models.Grid(self.app, show_squares=True))
        self.models.append(e2d_models.Water(self.app, waves_enabled=False))
        self.models.append(e2d_models.MainModel(self.app, vec2(-200, 20), vec2(200, 20), 40))

    def render(self) -> None:
        [model.render() for model in self.models]

    def update(self) -> None:
        [model.update() for model in self.models]
