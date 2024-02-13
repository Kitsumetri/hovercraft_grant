import pygame as pg

from typing import NoReturn
from pygame.math import Vector2 as vec2
from sys import stderr
from engine2d.scenes.scene import Scene


class Engine:
    def __init__(self, w: int = 700, h: int = 700,
                 window_name: str = 'Test Name') -> None:
        pg.init()

        self.screen_w: int = w
        self.screen_h: int = h
        self.win_name: str = window_name
        self.is_running: bool = True

        self.resolution: pg.math.Vector2 = vec2(w, h)
        self.clock: pg.time.Clock = pg.time.Clock()
        self.time = 0
        self.delta_time = 0

        self.screen: pg.Surface = pg.display.set_mode(self.resolution)

        pg.mouse.set_visible(False)

        self.scene = Scene(self)

    def get_time(self) -> None:
        self.time = pg.time.get_ticks() * 0.001

    def check_events(self) -> None:
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.is_running = False

    def fps(self) -> None:
        self.delta_time = self.clock.tick(60)
        fps = str((self.clock.get_fps()))
        pg.display.set_caption(f"{self.win_name} | FPS: {fps:.4}")

    def draw(self) -> None:
        self.screen.fill(pg.Color(90, 90, 90))  # dark gray color
        self.scene.render()

    def update(self) -> None:
        self.scene.update()
        pg.display.flip()

    def on_destroy(self) -> None:
        print(f'Destroying window {self.win_name}!', file=stderr)
        pg.quit()

    def run(self) -> NoReturn:
        while self.is_running:
            self.check_events()
            self.update()
            self.draw()
            self.fps()
        else:
            self.on_destroy()
