import glm
from typing import Tuple


class Light:
    def __init__(self, position: Tuple[float, float, float] = (50, 50, -10),
                 color: Tuple[float, float, float] = (1, 1, 1)):
        self.position: glm.vec3 = glm.vec3(position)
        self.color: glm.vec3 = glm.vec3(color)
        self.direction: glm.vec3 = glm.vec3(0, 0, 0)

        self.Ia: glm.vec3 = 0.06 * self.color  # ambient
        self.Id: glm.vec3 = 0.8 * self.color  # diffuse
        self.Is: glm.vec3 = 1.0 * self.color  # specular

        self.m_view_light: glm.mat4x4 = self.get_view_matrix()

    def get_view_matrix(self) -> glm.mat4x4:
        return glm.lookAt(self.position, self.direction, glm.vec3(0, 1, 0))
