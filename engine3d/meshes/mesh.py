from engine3d.graphics.texture import Texture
from engine3d.objects.vao import VAO


class Mesh:
    def __init__(self, app) -> None:
        self.app = app
        self.vao: VAO = VAO(app.ctx)
        self.texture: Texture = Texture(app)

    def release(self) -> None:
        self.vao.release()
        self.texture.release()

