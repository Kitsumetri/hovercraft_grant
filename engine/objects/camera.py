import glm
import pygame as pg
from engine.utils.constants import *


class Camera:
    def __init__(self, app, position: Tuple[float, float, float] = (0.0, 0.0, 4.0),
                 yaw: float = -90.0, pitch: float = 0.0) -> None:
        self.app = app
        self.aspect_ratio: float = app.screen_w / app.screen_h
        self.position: glm.vec3 = glm.vec3(position)
        self.up: glm.vec3 = glm.vec3(0, 1, 0)
        self.right: glm.vec3 = glm.vec3(1, 0, 0)
        self.forward: glm.vec3 = glm.vec3(0, 0, -1)
        self.yaw: float = yaw
        self.pitch: float = pitch

        self.m_view: glm.mat4x4 = self.get_view_matrix()
        self.m_proj: glm.mat4x4 = self.get_projection_matrix()

    def rotate(self) -> None:
        rel_x, rel_y = pg.mouse.get_rel()
        self.yaw += rel_x * SENSITIVITY
        self.pitch -= rel_y * SENSITIVITY
        self.pitch: float = max(-89.0, min(89.0, self.pitch))

    def update_camera_vectors(self) -> None:
        yaw: float = glm.radians(self.yaw)
        pitch: float = glm.radians(self.pitch)

        self.forward.x = glm.cos(yaw) * glm.cos(pitch)
        self.forward.y = glm.sin(pitch)
        self.forward.z = glm.sin(yaw) * glm.cos(pitch)

        self.forward: glm.vec3 = glm.normalize(self.forward)
        self.right: glm.vec3 = glm.normalize(glm.cross(self.forward, glm.vec3(0, 1, 0)))
        self.up: glm.vec3 = glm.normalize(glm.cross(self.right, self.forward))

    def update(self) -> None:
        self.move()
        self.rotate()
        self.update_camera_vectors()
        self.m_view = self.get_view_matrix()

    def move(self) -> None:
        velocity = SPEED * self.app.delta_time

        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            self.position += self.forward * velocity
        if keys[pg.K_s]:
            self.position -= self.forward * velocity
        if keys[pg.K_a]:
            self.position -= self.right * velocity
        if keys[pg.K_d]:
            self.position += self.right * velocity
        if keys[pg.K_q]:
            self.position += self.up * velocity
        if keys[pg.K_e]:
            self.position -= self.up * velocity

    def get_view_matrix(self) -> glm.mat4x4:
        return glm.lookAt(self.position, self.position + self.forward, self.up)

    def get_projection_matrix(self) -> glm.mat4x4:
        return glm.perspective(glm.radians(FOV), self.aspect_ratio, NEAR, FAR)
