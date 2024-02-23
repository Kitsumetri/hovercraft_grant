from pygame.math import Vector2 as vec2
from typing import List, Tuple, Union
import pygame as pg
import numpy as np


class BaseModel:
    def __init__(self, app) -> None:
        self.app = app
        self.center: vec2 = vec2(self.app.screen_w // 2, self.app.screen_h // 2)
        self.font_size: int = 20
        self.font_color: pg.Color = pg.Color('white')
        self.font: pg.font.Font = pg.font.Font(pg.font.get_default_font(), self.font_size)

    def render(self) -> None: ...

    def update(self) -> None: ...


class Grid(BaseModel):
    def __init__(self, app, show_squares: bool = False, square_size: int = 50) -> None:
        super().__init__(app)
        self.show_squares: bool = show_squares
        self.square_size: int = square_size
        self.grid_color: pg.Color = pg.Color(50, 50, 50, 0)
        self.color: pg.Color = pg.Color('white')

        self.x_axis: List[vec2] = [vec2(0, self.center.y), vec2(self.app.screen_w, self.center.y)]
        self.y_axis: List[vec2] = [vec2(self.center.x, 0), vec2(self.center.x, self.app.screen_h)]

        self.x_axis_text: pg.Surface = self.font.render('X', True, self.font_color)
        self.y_axis_text: pg.Surface = self.font.render('Y', True, self.font_color)

    def draw_basis(self) -> None:
        pg.draw.line(self.app.screen, self.color, self.x_axis[0], self.x_axis[1])
        pg.draw.line(self.app.screen, self.color, self.y_axis[0], self.y_axis[1])
        pg.draw.circle(self.app.screen, pg.Color('red'), self.center, 7)

        self.app.screen.blit(self.x_axis_text,
                             self.x_axis_text.get_rect(x=self.app.screen_w - self.font_size, y=self.center.y + self.font_size))

        self.app.screen.blit(self.y_axis_text,
                             self.y_axis_text.get_rect(x=self.center.x + self.font_size,
                                                       y=self.font_size))

    def draw_squares(self) -> None:
        for x in range(0, self.app.screen_w, self.square_size):
            pg.draw.line(self.app.screen, self.grid_color, (x, 0), (x, self.app.screen_h))

        for y in range(0, self.app.screen_h, self.square_size):
            pg.draw.line(self.app.screen, self.grid_color, (0, y), (self.app.screen_w, y))

    def render(self) -> None:
        if self.show_squares:
            self.draw_squares()
        self.draw_basis()


class Water(BaseModel):
    def __init__(self, app,
                 amplitudes: Union[List[float], None] = None,
                 lengths: Union[List[int], None] = None,
                 time_scale: float = 0.1,
                 waves_enabled: bool = True,
                 random_waves: bool = True) -> None:
        super().__init__(app)
        self.width: int = app.screen_w
        self.height: int = app.screen_h

        self.amplitudes: List[float] = amplitudes if amplitudes is not None else [20.0, 0.5]
        self.lengths: List[int] = lengths if lengths is not None else [100, 15]

        self.time_scale: float = time_scale
        self.time: float = 0

        self.waves_enabled: bool = waves_enabled
        self.random_waves: bool = random_waves

        self.water_color: pg.Color = pg.Color(0, 0, 255, 70)
        self.wave_color: pg.Color = pg.Color(0, 0, 255, 100)

    def create_wave(self, x: float, y: float) -> Tuple[float, float]:
        x_out, y_out = x, y

        for amp, length in zip(self.amplitudes, self.lengths):
            if self.random_waves:
                amp += np.random.uniform(-0.5, 0.5)
            x_out -= amp * np.sin(x / length - self.time / np.sqrt(length))
            y_out += amp * np.cos(x / length - self.time / np.sqrt(length))

        return x_out, y_out

    def render(self) -> None:
        if self.waves_enabled:
            points: List[Tuple[float, float]] = list()

            for x in range(-100, self.width+100, 2):
                wave_point = self.create_wave(x, self.height // 2 + 15)
                points.append(wave_point)

            mask: pg.Surface = pg.Surface((self.width, self.height), pg.SRCALPHA)
            mask.fill((0, 0, 0, 0))

            pg.draw.polygon(mask, self.water_color, points + [(self.width, self.height), (0, self.height)])

            self.app.screen.blit(mask, (0, 0))
            pg.draw.lines(self.app.screen, self.wave_color, False, points, 2)
        else:
            water_rect: pg.Surface = pg.Surface((self.width, self.height // 2), pg.SRCALPHA)
            water_rect.fill(self.water_color)
            self.app.screen.blit(water_rect, (0, self.height // 2))

    def update(self) -> None:
        self.time += self.time_scale

class Balloon:
    def __init__(self, app, radius: float, center: vec2, color: pg.Color) -> None:
        self.app = app
        self.center: vec2 = center
        self.radius: float = radius
        self.color: pg.Color = color
        self.surface = pg.Surface((radius * 2, radius * 2))
        self.mask = pg.mask.from_surface(self.surface)
        self.rect = self.surface.get_rect(center=center)

    def draw(self) -> None:
        pg.draw.circle(self.app.screen, self.color, self.center, self.radius, width=2)
        # pg.draw.rect(self.app.screen, pg.Color('black'), self.rect, width=2)

    def update(self) -> None: ...


class MainModel(BaseModel):
    def __init__(self, app, point_A: vec2, point_B: vec2, radius: float) -> None:
        super().__init__(app)

        self.point_A: vec2 = vec2(self.center.x + point_A.x,
                                  self.center.y - point_A.y)

        self.point_B: vec2 = vec2(self.center.x + point_B.x,
                                  self.center.y - point_B.y)

        self.radius: float = radius
        self.balloons_color: pg.Color = pg.Color('white')

        self.left_balloons: List[Balloon] = [Balloon(app, r, vec2(self.point_A.x, self.point_A.y + i * r * 2 + i * 6), self.balloons_color)
                                             for i, r in enumerate((self.radius, self.radius // 2, self.radius // 3), start=0)]

        self.right_balloons: List[Balloon] = [
            Balloon(app, r, vec2(self.point_B.x, self.point_B.y + i * r * 2 + i * 6), self.balloons_color)
            for i, r in enumerate((self.radius, self.radius // 2, self.radius // 3), start=0)]

        self.point_A_text: pg.Surface = self.font.render('A', True, self.font_color)
        self.point_B_text: pg.Surface = self.font.render('B', True, self.font_color)

        self.water = Water(app)

        self.t_values: List[float] = [0]
        self.y_values: List[float] = [0]
        self.dp_values: List[float] = [0]
        self.gamma_values: List[float] = [0]

    def update(self) -> None:
        super().update()
        # self.solve_system_euler()

    def render(self) -> None:
        pg.draw.line(self.app.screen, pg.Color('white'), self.point_A, self.point_B, width=5)

        pg.draw.circle(self.app.screen, pg.Color('black'), self.point_A, 5)
        self.app.screen.blit(self.point_A_text, vec2(self.point_A.x, self.point_A.y - self.font_size))

        pg.draw.circle(self.app.screen, pg.Color('black'), self.point_B, 5)
        self.app.screen.blit(self.point_B_text, vec2(self.point_B.x, self.point_B.y - self.font_size))

        [balloon.draw() for balloon in self.left_balloons]
        [balloon.draw() for balloon in self.right_balloons]
