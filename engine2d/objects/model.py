import pygame as pg
from pygame.math import Vector2 as vec2
from typing import List


class BaseModel:
    def __init__(self, app) -> None:
        self.app = app
        self.center: vec2 = vec2(self.app.screen_w // 2, self.app.screen_h // 2)
        self.font_size: int = 20
        self.font_color: pg.Color = pg.Color('white')
        self.font: pg.font.Font = pg.font.Font(pg.font.get_default_font(), self.font_size)

    def render(self) -> None:
        ...

    def update(self) -> None:
        ...


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
    def __init__(self, app):
        super().__init__(app)

        self.color = pg.Color(0, 0, 230, 45)
        self.surface_size = vec2(app.screen_w, app.screen_h // 2)
        self.surface = pg.Surface(self.surface_size, flags=pg.SRCALPHA)
        self.surface.fill(self.color)

        self.rect = self.surface.get_rect(x=0, y=self.surface_size.y)

    def render(self) -> None:
        self.app.screen.blit(self.surface, (0, self.surface_size.y))


class Balloon:
    def __init__(self, app, radius: float, center: vec2, color: pg.Color) -> None:
        self.app = app
        self.center: vec2 = center
        self.radius: float = radius
        self.color: pg.Color = color

    def draw(self) -> None:
        pg.draw.circle(self.app.screen, self.color, self.center, self.radius, width=2)

    def update(self) -> None:
        pass


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

        self.point_A_text = self.font.render('A', True, self.font_color)
        self.point_B_text = self.font.render('B', True, self.font_color)

    def render(self) -> None:
        pg.draw.line(self.app.screen, pg.Color('white'), self.point_A, self.point_B, width=5)

        pg.draw.circle(self.app.screen, pg.Color('black'), self.point_A, 5)
        self.app.screen.blit(self.point_A_text, vec2(self.point_A.x, self.point_A.y - self.font_size))

        pg.draw.circle(self.app.screen, pg.Color('black'), self.point_B, 5)
        self.app.screen.blit(self.point_B_text, vec2(self.point_B.x, self.point_B.y - self.font_size))

        [balloon.draw() for balloon in self.left_balloons]
        [balloon.draw() for balloon in self.right_balloons]






