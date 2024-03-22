from pygame.math import Vector2 as vec2
from typing import List, Tuple, Union
import pygame as pg
import numpy as np
from engine2d.utils.constants import *


class BaseModel:
    def __init__(self, app) -> None:
        self.app = app
        self.center_screen: vec2 = vec2(self.app.screen_w // 2, self.app.screen_h // 2)
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

        self.x_axis: List[vec2] = [vec2(0, self.center_screen.y), vec2(self.app.screen_w, self.center_screen.y)]
        self.y_axis: List[vec2] = [vec2(self.center_screen.x, 0), vec2(self.center_screen.x, self.app.screen_h)]

        self.x_axis_text: pg.Surface = self.font.render('X', True, self.font_color)
        self.y_axis_text: pg.Surface = self.font.render('Y', True, self.font_color)

    def draw_basis(self) -> None:
        pg.draw.line(self.app.screen, self.color, self.x_axis[0], self.x_axis[1])
        pg.draw.line(self.app.screen, self.color, self.y_axis[0], self.y_axis[1])
        pg.draw.circle(self.app.screen, pg.Color('red'), self.center_screen, 7)

        self.app.screen.blit(self.x_axis_text,
                             self.x_axis_text.get_rect(x=self.app.screen_w - self.font_size, y=self.center_screen.y + self.font_size))

        self.app.screen.blit(self.y_axis_text,
                             self.y_axis_text.get_rect(x=self.center_screen.x + self.font_size,
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


class Balloon(BaseModel):
    def __init__(self, app, radius: float, center: vec2, color: pg.Color, draw_hitbox: bool = False) -> None:
        super().__init__(app)
        self.app = app
        self.center: vec2 = center
        self.radius: float = radius
        self.color: pg.Color = color
        self.surface = pg.Surface((radius * 2, radius * 2))
        self.mask = pg.mask.from_surface(self.surface)
        self.rect = self.surface.get_rect(center=center)
        self.draw_hitbox = draw_hitbox

    def draw(self) -> None:
        pg.draw.circle(self.app.screen, self.color, self.center, self.radius, width=2)
        pg.draw.rect(self.app.screen, pg.Color('black'), self.rect, width=2) if self.draw_hitbox else None

    def update(self) -> None: ...

    def calculate_submerged_volume(self, water_level=500):
        R = self.radius / 10
        bottom_to_water = (self.center.y + R) - water_level
        if bottom_to_water <= 0:
            return 0  # Баллон не погружен

        h = min(2 * R, bottom_to_water)
        segment_area = R ** 2 * np.arccos((R - h) / R) - (R - h) * np.sqrt(2 * R * h - h ** 2)
        volume = segment_area
        return volume / 4

    def calculate_archimedes_force(self) -> float:
        if self.center.y <= self.center_screen.y - self.radius * 2:
            return 0
        volume = self.calculate_submerged_volume()  # объем погруженной части, м^3
        force = rho * g * volume
        return force


class MainModel(BaseModel):
    def __init__(self, app, point_A: vec2, point_B: vec2, radius: float) -> None:
        super().__init__(app)

        self.point_A: vec2 = vec2(self.center_screen.x + point_A.x,
                                  self.center_screen.y - point_A.y)

        self.point_B: vec2 = vec2(self.center_screen.x + point_B.x,
                                  self.center_screen.y - point_B.y)

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

        self.F_m = m * g
        self.dW_dt = 1.2
        self.dt = 0.01

    def update(self) -> None:
        super().update()
        self.solve_euler_equations()

    def solve_euler_equations(self):
        F_arch_sum = sum(b.calculate_archimedes_force() for b in self.left_balloons + self.right_balloons)

        dy_dt_square = (p * S - self.F_m + F_arch_sum) / m
        dp_dt = n * p_a / W * (Q_in - Q_out - self.dW_dt)
        d_gamma_dt_square = F_arch_sum * l * np.cos(alpha) / I

        self.y_values.append(self.y_values[-1] + dy_dt_square * self.dt)
        self.dp_values.append(self.dp_values[-1] + dp_dt * self.dt)
        self.gamma_values.append(self.gamma_values[-1] + d_gamma_dt_square * self.dt)

        print(f"Y: {self.y_values[-1]} | P: {self.dp_values[-1]} | Gamma: {self.gamma_values[-1]}")

    def render(self) -> None:
        pg.draw.line(self.app.screen, pg.Color('white'), self.point_A, self.point_B, width=5)

        pg.draw.circle(self.app.screen, pg.Color('black'), self.point_A, 5)
        self.app.screen.blit(self.point_A_text, vec2(self.point_A.x, self.point_A.y - self.font_size))

        pg.draw.circle(self.app.screen, pg.Color('black'), self.point_B, 5)
        self.app.screen.blit(self.point_B_text, vec2(self.point_B.x, self.point_B.y - self.font_size))

        [balloon.draw() for balloon in self.left_balloons + self.right_balloons]
