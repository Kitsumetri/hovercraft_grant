import pygame as pg
import moderngl as mgl

from sys import stderr
from pygame.math import Vector2 as vec2
from typing import NoReturn
from platform import system
from engine3d.meshes.mesh import Mesh
from engine3d.scenes.scene import Scene
from engine3d.objects.camera import Camera
from engine3d.objects.light import Light
from engine3d.utils.constants import *


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
        self.time: float = 0.0
        self.delta_time: int = 0

        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)

        if system() == 'Darwin':
            pg.display.gl_set_attribute(pg.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, True)

        pg.display.gl_set_attribute(pg.GL_DEPTH_SIZE, 24)

        self.screen: pg.Surface = pg.display.set_mode(self.resolution,
                                                      flags=pg.OPENGL | pg.DOUBLEBUF)

        pg.event.set_grab(True)
        pg.mouse.set_visible(False)

        self.ctx: mgl.Context = mgl.create_context()
        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)
        self.ctx.gc_mode = 'auto'

        self.light: Light = Light()
        self.camera: Camera = Camera(self)
        self.mesh: Mesh = Mesh(self)
        self.scene: Scene = Scene(self)

    def get_time(self) -> None:
        self.time: float = pg.time.get_ticks() * 0.001

    def check_events(self) -> None:
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.is_running: bool = False

    def fps(self) -> None:
        self.delta_time: int = self.clock.tick(60)
        fps: float = (self.clock.get_fps())
        pg.display.set_caption(f"{self.win_name} | FPS: {fps:.4}")

    def update(self) -> None:
        self.ctx.clear(color=BG_COLOR)
        self.scene.render()
        self.camera.update()
        pg.display.flip()

    def on_destroy(self) -> None:
        self.mesh.release()
        print(f'Destroying window {self.win_name}!', file=stderr)
        pg.quit()

    def run(self) -> NoReturn:
        while self.is_running:
            self.check_events()
            self.update()
            self.fps()
        else:
            self.on_destroy()
