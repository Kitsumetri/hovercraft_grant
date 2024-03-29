import moderngl as mgl
import glm
import pygame as pg
from typing import Tuple
from engine3d.objects.camera import Camera
from engine3d.graphics.texture import Texture


class BaseModel:
    def __init__(self, app, vao_name: str, tex_id: str,
                 pos: Tuple[int, int, int] = (0, 0, 0),
                 rot: Tuple[int, int, int] = (0, 0, 0),
                 scale: Tuple[float, float, float] = (1, 1, 1)) -> None:

        self.app = app
        self.pos: glm.vec3 = glm.vec3(pos)
        self.vao_name: str = vao_name
        self.rot: glm.vec3 = glm.vec3([glm.radians(a) for a in rot])
        self.scale: Tuple[float, float, float] = scale
        self.m_model: glm.mat4x4 = self.get_model_matrix()
        self.tex_id: str = tex_id
        self.vao: mgl.VertexArray = app.mesh.vao.vaos[vao_name]
        self.program: mgl.Program = self.vao.program
        self.camera: Camera = self.app.camera

        self.texture: Texture | None = None

    def update(self) -> None: ...

    def get_model_matrix(self) -> glm.mat4x4:
        m_model: glm.mat4x4 = glm.mat4()

        m_model: glm.mat4x4 = glm.translate(m_model, self.pos)

        m_model: glm.mat4x4 = glm.rotate(m_model, self.rot.z, glm.vec3(0, 0, 1))
        m_model: glm.mat4x4 = glm.rotate(m_model, self.rot.y, glm.vec3(0, 1, 0))
        m_model: glm.mat4x4 = glm.rotate(m_model, self.rot.x, glm.vec3(1, 0, 0))

        m_model: glm.mat4x4 = glm.scale(m_model, self.scale)
        return m_model

    def render(self) -> None:
        self.update()
        self.vao.render()


class ExtendedBaseModel(BaseModel):
    def __init__(self, app, vao_name: str, tex_id: str,
                 pos: Tuple[int, int, int] = (0, 0, 0),
                 rot: Tuple[int, int, int] = (0, 0, 0),
                 scale: Tuple[float, float, float] = (1, 1, 1)) -> None:
        super().__init__(app, vao_name, tex_id, pos, rot, scale)
        self.depth_texture = None

        self.on_init()

    def update(self) -> None:
        self.texture.use(location=0)
        self.program['camPos'].write(self.camera.position)
        self.program['m_view'].write(self.camera.m_view)
        self.program['m_model'].write(self.m_model)

    def update_shadow(self) -> None:
        self.program['m_model'].write(self.m_model)

    def on_init(self) -> None:
        # texture
        self.texture: mgl.Texture = self.app.mesh.texture.textures[self.tex_id]
        self.program['u_texture_0'] = 0
        self.texture.use(location=0)

        self.depth_texture: mgl.Texture = self.app.mesh.texture.textures['depth_texture']
        self.depth_texture.use(location=1)

        # mvp
        self.program['m_proj'].write(self.camera.m_proj)
        self.program['m_view'].write(self.camera.m_view)
        self.program['m_model'].write(self.m_model)

        # light
        self.program['light.position'].write(self.app.light.position)
        self.program['light.Ia'].write(self.app.light.Ia)
        self.program['light.Id'].write(self.app.light.Id)
        self.program['light.Is'].write(self.app.light.Is)


class SkyBox(BaseModel):
    def __init__(self, app, vao_name: str = 'skybox', tex_id: str = 'skybox',
                 pos: Tuple[int, int, int] = (0, 0, 0), rot: Tuple[int, int, int] = (0, 0, 0),
                 scale: Tuple[int, int, int] = (1, 1, 1)) -> None:
        super().__init__(app, vao_name, tex_id, pos, rot, scale)
        self.on_init()

    def update(self) -> None:
        self.program['m_view'].write(glm.mat4(glm.mat3(self.camera.m_view)))

    def on_init(self) -> None:
        self.texture: mgl.TextureCube = self.app.mesh.texture.textures[self.tex_id]
        self.program['u_texture_skybox'] = 0
        self.texture.use(location=0)

        self.program['m_proj'].write(self.camera.m_proj)
        self.program['m_view'].write(glm.mat4(glm.mat3(self.camera.m_view)))


class Cube(ExtendedBaseModel):
    def __init__(self, app, vao_name='cube', tex_id=0, pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)) -> None:
        super().__init__(app, vao_name, tex_id, pos, rot, scale)


class Hovercraft(ExtendedBaseModel):
    def __init__(self, app, vao_name='hovercraft', tex_id='hovercraft',
                 pos=(0, 0, 0), rot=(-90, 0, 0), scale=(1, 1, 1)) -> None:
        super().__init__(app, vao_name, tex_id, pos, rot, scale)

        self.velocity: glm.vec3 = glm.vec3(0, 0, 0)
        self.acceleration: float = 0.01
        self.max_speed: float = 0.5
        self.brake_factor: float = 0.95

        self.angular_velocity: glm.vec3 = glm.vec3(0, 0, 0)
        self.angular_acceleration: glm = 0.001
        self.max_angular_speed: int = 2
        self.angular_brake_factor: float = 0.95

    def update(self) -> None:
        super().update()
        self.move()

    def move(self) -> None:
        keys: pg.key.ScancodeWrapper = pg.key.get_pressed()

        if keys[pg.K_LEFT]:
            self.angular_velocity.y += self.angular_acceleration
        if keys[pg.K_RIGHT]:
            self.angular_velocity.y -= self.angular_acceleration
        if keys[pg.K_UP]:
            self.velocity.z -= self.acceleration
        if keys[pg.K_DOWN]:
            self.velocity.z += self.acceleration

        self.velocity *= self.brake_factor
        self.angular_velocity *= self.angular_brake_factor

        self.velocity.z = glm.clamp(self.velocity.z, -self.max_speed, self.max_speed)
        self.angular_velocity.y = glm.clamp(self.angular_velocity.y, -self.max_angular_speed, self.max_angular_speed)

        rotation_matrix: glm.mat4x4 = glm.rotate(glm.mat4(1.0), self.rot.y, glm.vec3(0, 1, 0))
        rotated_velocity: glm.vec3 = glm.vec3(rotation_matrix * glm.vec4(self.velocity, 1.0))

        self.pos += rotated_velocity
        self.rot.y += self.angular_velocity.y

        self.m_model: glm.mat4x4 = self.get_model_matrix()
